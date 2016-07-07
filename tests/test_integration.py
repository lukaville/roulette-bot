import unittest

from i18n import _
from util.base_test_case import IntegrationTestCase


class TestRoulettegram(IntegrationTestCase):
    def test_start(self):
        self.send_message('/start', skip_answer=False)
        self.verify_answer(_('START'))

    def test_roulette_start(self):
        self.send_message('/start')
        self.send_message('/roulette', skip_answer=False)
        self.verify_answer(_('SEARCHING'))

    def test_roulette_connect(self):
        self.send_message('/start', from_user_id=1)
        self.send_message('/start', from_user_id=2)

        self.send_message('/roulette', from_user_id=1)
        self.send_message('/roulette', from_user_id=2, skip_answer=False)
        self.verify_answer(_('ESTABLISHED'), to_user_id=2)
        self.verify_answer(_('ESTABLISHED'), to_user_id=1)

    def test_roulette_messaging(self):
        self.send_message('/start', from_user_id=1)
        self.send_message('/start', from_user_id=2)

        self.send_message('/roulette', from_user_id=1)
        self.send_message('/roulette', from_user_id=2)

        # Send message and skip connection established message
        self.send_message('test', from_user_id=1, skip_answer=True)
        self.verify_answer(_('MESSAGE_BODY') % 'test', to_user_id=2)

        self.send_message('abc', from_user_id=2, skip_answer=False)
        self.verify_answer(_('MESSAGE_BODY') % 'abc', to_user_id=1)

    def test_roulette_disconnection(self):
        # Connect 1 and 2
        self.send_message('/start', from_user_id=1)
        self.send_message('/start', from_user_id=2)

        self.send_message('/roulette', from_user_id=1)
        self.send_message('/roulette', from_user_id=2)

        # Skip connection established message
        self.skip_answer()

        # Verify disconnection
        self.send_message('/roulette', from_user_id=1, skip_answer=False)
        self.verify_answer(_('DISCONNECTED_SEARCH_NEW'), to_user_id=1)
        self.verify_answer(_('DISCONNECTED'), to_user_id=2)
        self.verify_answer(_('SEARCHING'), to_user_id=1)

        self.send_message('abc', from_user_id=1, skip_answer=False)
        self.verify_answer(_('ERROR_SEARCHING'), to_user_id=1)

        self.send_message('abc', from_user_id=2, skip_answer=False)
        self.verify_answer(_('ERROR_IDLE'), to_user_id=2)

    def test_roulette_continue_with_third(self):
        # Connect 1 and 2
        self.send_message('/start', from_user_id=1)
        self.send_message('/start', from_user_id=2)

        self.send_message('/roulette', from_user_id=1)
        self.send_message('/roulette', from_user_id=2)
        self.skip_answer()

        # Restart 1 (and disconnect 2)
        self.send_message('/roulette', from_user_id=1)
        self.skip_answer()
        self.skip_answer()

        # Connect 3 (to 1)
        self.send_message('/start', from_user_id=3)
        self.send_message('/roulette', from_user_id=3, skip_answer=False)

        self.verify_answer(_('ESTABLISHED'), to_user_id=3)
        self.verify_answer(_('ESTABLISHED'), to_user_id=1)


if __name__ == '__main__':
    unittest.main()
