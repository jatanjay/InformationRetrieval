jatan pandya 446 | Readme


1. Run your program with fancy tokenization, stopping, and Porter stemming on sense-and-sensibility.gz and look at 
the -tokens.txt -stats.txt file to see the most frequent terms from Sense and Sensibility. 
Are the top terms relevant to the story or do they seem like everyday words that aren't particularly to the novel? 
Support your answer with examples. You may find it useful to skim the summary on Wikipedia to know what words are part of the story.

>> Yes. If we look at the top hits, (after skimming through the pronouns etc.) they are ’elinor’, ’marianne’, ’dashwood’, "edward",
"willoughbi", etc. Which are the characters of the story hence relevant.

2. Are there any of those top terms that should have been stopwords? 
Do the top terms or the list of all tokens suggest any changes to the tokenizing or stemming rules? 
What are they and why should they be made?
>> Yes, I do see a lot of possible contenders for stopwords. They include pronouns, and other functional words like not, could, shall etc.
I don't think any big changes have to be made for stopwords, since there isn't any one size fits all solutions to begin with. Hence it comes down to the researcher to see what stop words are contributing little or less and can then make a judgement based on their needs. 
Coming to tokenizing and stemming, I don't think anything is necessary, it does a pretty good job right now (even though we just implemented till 1_c)


Figure 4.4. in the textbook (p. 82) displays a graph of vocabulary growth for the TREC GOV2 collection. 
Create a similar graph for Sense and Sensibility and upload an image of your graph. 
Note that you should be able to use the -heaps.txt file to generate the graph.
>> uploaded as heaps.png

Does Sense and Sensibility follow Heaps Law? Why do you think so or think not?
>> Yes. It does. We know Heap's Law states that "the vocabulary size of a text grows sub-linearly with its total word count". looking at the plot, we see this holds true. As to "why", I'm afraid it being an empircal law I don't have an exact response. Coming to SAS, it's good news it does follow heaps law, follows the same "language model" we humans use.