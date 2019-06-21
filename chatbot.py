class CustomChatBot(ChatBot):

    def __init__(self, bot_conf, **kwargs):
        bot_db_kwargs = {
            'pk': bot_conf.pk,
            'input_adapter': bot_conf.input_adapter,
            'output_adapter': bot_conf.output_adapter,
            'trainer': bot_conf.trainer,
            'logic_adapters': bot_conf.logic_adapters
        }
        for kw in bot_db_kwargs.copy():
            if kw in kwargs:
                bot_db_kwargs.pop(kw)
        kwargs.update(bot_db_kwargs)
        self.pk = kwargs.get('pk')
        super(CustomChatBot, self).__init__(bot_conf.name, **kwargs)

    def get_response(self, input_item, conversation_id=None):
        if not conversation_id:
            if not self.default_conversation_id:
                self.default_conversation_id = self.storage.create_conversation(bot_id=self.pk)
            conversation_id = self.default_conversation_id
        input_statement = self.input.process_input_statement(input_item)

        # Preprocess the input statement
        for preprocessor in self.preprocessors:
            input_statement = preprocessor(self, input_statement)

        statement, response = self.generate_response(input_statement, conversation_id)

        # Learn that the user's input was a valid response to the chat bot's previous output
        previous_statement = self.storage.get_latest_response(conversation_id)

        if not self.read_only:
            self.learn_response(statement, previous_statement)
            self.storage.add_to_conversation(conversation_id, statement, response)

        dialog = [input_item, response.text]
        self.storage.save_conversation_activity(conversation_id, dialog)

        # Process the response output with the output adapter
        return self.output.process_response(response, conversation_id)


class ChatBotBuilder(object):

    def __init__(self, bot_conf=None, **kwargs):
        self.bot_conf = bot_conf

    def get_bot(self, **kwargs):
        if self.bot_conf:
            bot = CustomChatBot(self.bot_conf)
        else:
            bot = ChatBot(**kwargs)
        return bot
