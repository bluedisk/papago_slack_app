import json
from django.test import TestCase
from papago_slack import papago

# def sanitize(blocks: dict) -> (List[str], str):
# def recognize_language(text: str) -> (str, str):
# def custom_translate(sanitized_text: str) -> str:
# def desanitize(extra_list: List[str], translated: str) -> str:

BLOCKS1 = """
      [{
        "block_id": "WBW/j",
        "elements": [
          {
            "elements": [
              {
                "text": "파파고 ",
                "type": "text"
              },
              {
                "type": "user",
                "user_id": "UFGQX1QFK"
              },
              {
                "text": "  바보 ",
                "type": "text"
              },
              {
                "type": "link",
                "url": "https://google.com"
              },
              {
                "text": " 다람쥐 ",
                "type": "text"
              },
              {
                "name": "smirk",
                "type": "emoji"
              }
            ],
            "type": "rich_text_section"
          }
        ],
        "type": "rich_text"
      }]
      """


class ParserTestCase(TestCase):
    def test_sanitizing(self):
        extra_list, text = papago.sanitize(json.loads(BLOCKS1))
        self.assertEqual(text, "파파고 [1]  바보 [2] 다람쥐 [3]")
        self.assertListEqual(extra_list, [('user', 'UFGQX1QFK'), ('link', "https://google.com"), ('emoji', 'smirk')])

        text = papago.desanitize(extra_list, text)
        self.assertEqual(text, "파파고 <@UFGQX1QFK>  바보 <https://google.com> 다람쥐 :smirk:")

    def text_language_detection(self):
        from_lang, to_lang = papago.recognize_language('파파고\xa0<@UFGQX1QFK>\xa0\xa0바보\xa0<https://google.com>\xa0다람쥐\xa0:smirk:')
        self.assertEqual(from_lang, 'ko')
        self.assertEqual(from_lang, 'en')

