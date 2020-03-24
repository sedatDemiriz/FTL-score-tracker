from TwitchWebsocket import TwitchWebsocket
import logging as lg
import pandas as pd
import sys
import re

class ftlScoreBot:
    def __init__(self, channel):
        self.host = "irc.chat.twitch.tv"
        self.port = 6667
        self.chan = "#" + str(channel)
        self.nick = "ftltrackerbot"
        self.auth = "oauth:19wyalzmxpekmfvne7off4l0y21jy5"
        
        # Send along all required information, and the bot will start 
        # sending messages to your callback function. (self.message_handler in this case)
        self.ws = TwitchWebsocket(host=self.host, 
                                  port=self.port,
                                  chan=self.chan,
                                  nick=self.nick,
                                  auth=self.auth,
                                  callback=self.message_handler,
                                  capability=["membership", "tags", "commands"],
                                  live=True)

        # Temporary dataframe for storing score guesses                                  
        self.df = pd.DataFrame(columns=['User', 'Score'])

        # Patterns for score guesses and commands
        self.num_pat = re.compile('^[0-9]+')
        self.com_pat = re.compile('!score [0-9]+')

        # Initialize bot function
        logger.info('Connected to channel: '+ self.chan)
        self.ws.start_bot()
        
        # Any code after this will be executed after a KeyboardInterrupt
        logger.info('Shutting bot down.')

    # Check if user is Moderator+
    def check_user_hard(self, m):
        return ("moderator" in m.tags["badges"] or "broadcaster" in m.tags["badges"] or "bloodlad_" == m.user.lower())

    # Display winner
    def report_winner(self, username, score):
        logger.info('Reporting winner: %s.', username)
        self.ws.send_message("Winner: " + username + " with " + str(score))

    # Drop all values in given table
    def drop_all(self, df):
        self.df = df.iloc[0:0]

    # Calculate score differences
    def score_calc_reg(self, df, correct):

        logger.info('Calculating score differences: regular rules.')
        df['Diff'] = abs(df['Score'] - correct)
        df = df.sort_values('Diff')

        return df

    # Calculate score differences using price is right rules
    def score_calc_price(self, df, correct):
        
        logger.info('Calculating score differences: price-is-right rules.')
        df['Diff'] = correct - df['Score']
        df = df[df['Diff'] >= 0]
        df = df.sort_values('Diff')

        return df

    # Handle score guesses and tally
    def message_handler(self, m):

        # Ignore network based errors
        try:                    

            # Check for patterns in message
            match = self.num_pat.match(m.message)
            command = self.com_pat.match(m.message)
            
            # If a user guess is identified
            if match:

                # Localize variables with appropriate typing
                score = int(match.group())
                username = str(m.user)
                logger.info('Got a score guess: %d.', score)                

                if username in self.df.User.values:
                    # If guess is from the same user, replace existing guess
                    self.df.loc[(self.df.User == username), 'Score'] = score
                    logger.info('Replacing score guess from user: %s.', username)
                else:
                    # Otherwise, add to the list
                    self.df = self.df.append({'User': username, 'Score': score}, ignore_index=True)
                    logger.info('Adding score guess from user: %s.', username)
            
            # If Moderator+ have put in correct score
            elif command and self.check_user_hard(m) and len(self.df):
                # Get correct score
                correct = int(re.split(' ', command.group())[1])
                logger.info('Recieved correct score: %d.', correct)
                
                # Decide what rules channel uses
                if not (channel2join in price):
                    # Get differences from the correct score
                    self.df = self.score_calc_reg(self.df, correct)
                    
                    # Display winner
                    self.report_winner(self.df['User'].iloc[0], self.df['Score'].iloc[0])
                    
                else:
                    # Get differences from the correct score
                    self.df = self.score_calc_price(self.df, correct)

                    # If there are valid guesses, display winner
                    if len(self.df):                        
                        self.report_winner(self.df['User'].iloc[0], self.df['Score'].iloc[0])

                        # Drop all entries, guesses have ended
                        self.drop_all(self.df)
                        logger.info('Dropping all guesses from current round.')
                    
                    # If no positive differences, report
                    else:                        
                        logger.info('No guesses under the correct score.')
                        self.ws.send_message('Nobody has guessed low enough.')                

            else:
                # logger.info('Message didn\'t match any pattern.')
                pass  
                
        except:
            logger.info('Encountered an error: '+ str(sys.exc_info()[0]))

# Start bot when launched from CLI
if __name__ == "__main__":
    
    # Channels using Price-is-Right rules
    price = ['necrorebel']

    # Logging setup
    lg.basicConfig(level = lg.INFO)
    logger = lg.getLogger(__name__)
    logger.info('Launching bot.')

    # Get the channel to join
    channel2join = sys.argv[1]

    # Launch bot
    ftlScoreBot(channel2join)