import logging
import re
import google.generativeai as genai
import keys

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Configure Gemini client
genai.configure(api_key=keys.GOOGLE_API_KEY)

def format_string(text):
    """Removes newlines and other characters that can interfere with speech."""
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'[\*#]', '', text) # Remove markdown-like characters
    return text

def get_gemini_response(history, question):
    """Interacts with the Gemini API and returns the response and updated history."""
    model = genai.GenerativeModel(
        model_name=keys.MODEL,
        system_instruction=keys.SYSTEM_MESSAGE
    )
    chat = model.start_chat(history=history)
    response = chat.send_message(question)
    
    speak_output = format_string(response.text)
    
    # Convert Content objects to a JSON-serializable list of dicts
    updated_history = []
    for content in chat.history:
        # Assuming simple text parts for now
        parts = [part.text for part in content.parts]
        updated_history.append({'role': content.role, 'parts': parts})

    # Trim history
    if len(updated_history) > keys.MAX_CONVERSATION_HISTORY:
        updated_history = updated_history[-keys.MAX_CONVERSATION_HISTORY:]
        
    return speak_output, updated_history

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "ようこそ。何が知りたいですか？"
        return (
            handler_input.response_builder
                .speak(speak_output)
                .reprompt(speak_output)
                .response
        )

class ChatGPTIntentHandler(AbstractRequestHandler):
    """Handler for ChatGPT Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("ChatGPTIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        session_attr = handler_input.attributes_manager.session_attributes
        
        if "history" not in session_attr:
            session_attr["history"] = []

        question = handler_input.request_envelope.request.intent.slots["question"].value
        
        try:
            speak_output, updated_history = get_gemini_response(session_attr["history"], question)
            session_attr["history"] = updated_history
        except Exception as e:
            logger.error(f"Error calling Gemini: {e}")
            speak_output = "すみません、うまく聞き取れませんでした。もう一度お願いします。"
            
        return (
            handler_input.response_builder
                .speak(speak_output)
                .reprompt("他に質問はありますか？")
                .response
        )

class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "なにか質問をしてみてください。"
        return (
            handler_input.response_builder
                .speak(speak_output)
                .reprompt(speak_output)
                .response
        )

class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Handler for Cancel and Stop Intents."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (
            is_intent_name("AMAZON.CancelIntent")(handler_input) or
            is_intent_name("AMAZON.StopIntent")(handler_input)
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "さようなら"
        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    """Handler for Fallback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = "すみません、よくわかりませんでした。もう一度試してください。"
        reprompt = "もう一度試してください。"
        return handler_input.response_builder.speak(speech).reprompt(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        # Any cleanup logic goes here.
        return handler_input.response_builder.response

class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = handler_input.request_envelope.request.intent.name
        speak_output = f"You just triggered {intent_name}"
        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors."""
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)
        speak_output = "すみません、エラーが発生しました。もう一度お試しください。"
        return (
            handler_input.response_builder
                .speak(speak_output)
                .reprompt(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill.
sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(ChatGPTIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

handler = sb.lambda_handler()
