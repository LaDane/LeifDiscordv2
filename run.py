# must install OpenJDK 13.0.2 and Lavalink #1163
# navigate to OpenJDK bin folder
# java -jar Lavalink.jar

from bot import DiscordLeif

def main():
    bot = DiscordLeif()
    bot.run()

if __name__ == "__main__":
    main()