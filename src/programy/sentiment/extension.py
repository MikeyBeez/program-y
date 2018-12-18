"""
Copyright (c) 2016-2018 Keith Sterling http://www.keithsterling.com

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

This is an example extension that allow you to call an external service to retreive the energy consumption data
of the customer. Currently contains no authentication
"""

from programy.utils.logging.ylogger import YLogger

from programy.extensions.base import Extension

class SentimentExtension(Extension):

    def _check_enabled(self, context):
        if context.bot.sentiment_analyser is not None:
            return "SENTIMENT ENABLED"
        else:
            return "SENTIMENT DISABLED"

    def _calc_conversation_sentiment(self, context):
        conversation = context.bot.get_conversation(context)
        positivity, subjectivity = conversation.calculate_sentiment_score()
        if context.bot.sentiment_scores is not None:
            pos_str = context.bot.sentiment_scores.positivity(positivity)
            sub_str = context.bot.sentiment_scores.subjectivity(positivity)
            return "SENTIMENT FEELING %s AND %s"%(pos_str, sub_str)
        return "SENTIMENT FEELING NEUTRAL AND NEUTRAL"

    def _calc_question_sentiment(self, context, nth_question):
        return "SENTIMENT FEELING NEUTRAL AND NEUTRAL"

    def _calc_feeling(self, context, words):
        if context.bot.sentiment_analyser is not None:

            if len(words) >= 3:
                if words[2] == 'LAST':
                    if len(words) == 4:
                        if words[3].isdigit():
                            return self._calc_question_sentiment(context, int(words[3]))

                elif words[2] == 'OVERALL':
                    return self._calc_conversation_sentiment(context)

            return "SENTIMENT INVALID COMMAND"

        else:
            return "SENTIMENT DISABLED"

    def _calc_score(self, context, words):
        if context.bot.sentiment_analyser is not None:

            text = " ".join(words[2:])

            positivity, subjectivity = context.bot.sentiment_analyser.analyse_all(text)

            pos_str = "UNKNOWN"
            subj_str = "UNKNOWN"
            if context.bot.sentiment_scores is not None:
                pos_str = context.bot.sentiment_scores.positivity(positivity, context)
                subj_str = context.bot.sentiment_scores.subjectivity(positivity, context)

            return "SENTIMENT SCORES POSITIVITY %s SUBJECTIVITY %s" % (pos_str, subj_str)

        else:
            return "SENTIMENT DISABLED"

    # execute() is the interface that is called from the <extension> tag in the AIML
    def execute(self, context, data):
        YLogger.debug(context, "Sentiment - Calling external service for with extra data [%s]", data)

        # SENTIMENT SCORE <TEXT STRING>

        words = data.split(" ")
        if words:

            if words[0] == "SENTIMENT":

                if len(words) >= 2:
                    if words[1] == "SCORE":
                        return self._calc_score(context, words)

                    if words[1] == "FEELING":
                        return self._calc_feeling(context, words)

                    if words[1] == 'ENABLED':
                        return self._check_enabled(context)

        return "SENTIMENT INVALID COMMAND"
