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
              },
              {
                "channel_id": "C0166CJGQ2F",
                "type": "channel"
              },
              {
                "range": "here",
                "style": {"bold": true},    
                "type": "broadcast"
              }
            ],
            "type": "rich_text_section"
          }
        ],
        "type": "rich_text"
      }]
      """

TEXT1="""<!subteam^SRS1R1BNW|@frontend> it's a test in <!here> for <https://google.com|test>
if you know about <@UFGQX1QFK> or <#C0166CJGQ2F|test2> please talk to me :smirk: and `test code`
"""

class ParserTestCase(TestCase):
    def test_block_sanitizing(self):
        extra_list, text = papago.sanitize_block(json.loads(BLOCKS1))
        self.assertEqual(text, "파파고 [1]  바보 [2] 다람쥐 [3][4][5]")
        self.assertListEqual(extra_list, [
            ('user', 'UFGQX1QFK'),
            ('link', "https://google.com"),
            ('emoji', 'smirk'),
            ('channel', 'C0166CJGQ2F'),
            ('broadcast', 'here')
        ])

        text = papago.desanitize(text, elements=extra_list)
        self.assertEqual(text, "파파고 <@UFGQX1QFK>  바보 <https://google.com> 다람쥐 :smirk:<#C0166CJGQ2F><!here>")

    def test_text_sanitizing(self):
        extras, text, letters = papago.sanitize_text(TEXT1)
        self.assertEqual(text, "[1] it's a test in [2] for [3]\nif you know about [4] or [5] please talk to me [6] and [7]\n")
        self.assertEqual(letters, "itsatestinforifyouknowaboutorpleasetalktomeand")
        self.assertListEqual(extras, [
            "<!subteam^SRS1R1BNW|@frontend>",
            "<!here>",
            "<https://google.com|test>",
            "<@UFGQX1QFK>",
            "<#C0166CJGQ2F|test2>",
            ':smirk:',
            '`test code`'
        ])

        text = papago.desanitize(text, extras)
        self.assertEqual(text, TEXT1)

    def text_language_detection(self):
        from_lang, to_lang = papago.recognize_language('파파고\xa0<@UFGQX1QFK>\xa0\xa0바보\xa0<https://google.com>\xa0다람쥐\xa0:smirk:')
        self.assertEqual(from_lang, 'ko')
        self.assertEqual(from_lang, 'en')

