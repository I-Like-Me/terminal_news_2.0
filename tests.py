import os
os.environ['DATBASE_URL'] = 'sqlite://'

import unittest
from app import app, db
from app.models import User, Character

class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username='leenik')
        u.set_password('tony')
        self.assertFalse(u.check_password('not tony'))
        self.assertTrue(u.check_password('tony'))

    def test_avatar(self):
        u = User(username='john', email='john@example.com')
        self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/d4c74594d841139328695756648b6bd6?d=identicon&s=128'))

    def test_team(self):
        u1 = User(username='leenik', email='leenik@mynock.sw')
        u2 = User(username='bacta', email='bacta@mynock.sw')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertEqual(u1.team.all(), [])
        self.assertEqual(u1.teammates.all(), [])

        u1.join_team(u2)
        db.session.commit()
        self.assertTrue(u1.in_team_with(u2))
        self.assertEqual(u1.team.count(), 1)
        self.assertEqual(u1.team.first().username, 'bacta')
        self.assertEqual(u2.teammates.count(), 1)
        self.assertEqual(u2.teammates.first().username, 'leenik')

        u1.leave_team(u2)
        db.session.commit()
        self.assertFalse(u1.in_team_with(u2))
        self.assertEqual(u1.team.count(), 0)
        self.assertEqual(u2.teammates.count(), 0)

    def test_team_characters(self):
        u1 = User(username='leenik', email='leenik@mynock.sw')
        u2 = User(username='bacta', email='bacta@mynock.sw')
        u3 = User(username='tryst', email='tryst@mynock.sw')
        u4 = User(username='lynn', email='lynn@mynock.sw')
        db.session.add_all([u1, u2, u3, u4])

        c1 = Character(name='johnny', player=u1)
        c2 = Character(name='james', player=u2)
        c3 = Character(name='jpc', player=u3)
        c4 = Character(name='kat', player=u4)
        db.session.add_all([c1, c2, c3, c4])
        db.session.commit()

        u1.join_team(u2)
        u1.join_team(u4)
        u2.join_team(u3)
        u3.join_team(u4)
        db.session.commit()

        tm1 = u1.team_characters().all()
        tm2 = u2.team_characters().all()
        tm3 = u3.team_characters().all()
        tm4 = u4.team_characters().all()
        self.assertEqual(tm1, [c4, c1, c2])
        self.assertEqual(tm2, [c3, c2])
        self.assertEqual(tm3, [c4, c3])
        self.assertEqual(tm4, [c4])

if __name__ == '__main__':
    unittest.main(verbosity=2)