import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
nltk.download('vader_lexicon')

def main():
    contentBytes = store.Get('start') #this is a bytes 
    
    res = {}
    content = contentBytes["start"]
    sia = SentimentIntensityAnalyzer()
    score = sia.polarity_scores(content)
    res['sentiment'] = score
    store.Put('sentiment',res)