import itertools

from flask.ext.babel import _

from skylines.lib.decorators import reify


class FlightAchievementDataCollector(object):
    """Collect information useful for detecting achievements.

    """
    def __init__(self, flight):
        self.flight = flight

    @reify
    def triangle_distance(self):
        if not self.flight.olc_triangle_distance:
            return 0
        return self.flight.olc_triangle_distance / 1000

    @reify
    def duration(self):
        """Duration in hours"""
        return self.flight.duration.total_seconds() / 3600


class SkylinesAchievementDataCollector(object):
    """Collect statistics about skylines-related user activity
    """

    def __init__(self, user):
        self.user = user

    @reify
    def tracks_uploaded(self):
        from skylines.model.igcfile import IGCFile
        return IGCFile.query().filter_by(owner=self.user).count()

    @reify
    def users_followed(self):
        from skylines.model.follower import Follower
        return Follower.query().filter_by(source=self.user).count()

    @reify
    def followers_attracted(self):
        from skylines.model.follower import Follower
        return Follower.query().filter_by(destination=self.user).count()

    @reify
    def comments_made(self):
        from skylines.model.flight_comment import FlightComment
        return FlightComment.query().filter_by(user=self.user).count()


class Achievement(object):
    def __init__(self, name, **params):
        self.name = name
        self.params = params

    def is_achieved(self, context):
        raise NotImplementedError  # pragma: no cover

    @property
    def title(self):
        raise NotImplementedError  # pragma: no cover

    def __repr__(self):
        return "<Achievement %s: '%s'>" % (self.name, self.title)


class TriangleAchievement(Achievement):
    @property
    def title(self):
        return _("Triangle of more than %(distance)s km", **self.params)

    def is_achieved(self, context):
        return context.triangle_distance >= self.params['distance']


class DurationAchievement(Achievement):
    @property
    def title(self):
        return _("Flight duration of more than %(duration)s h", **self.params)

    def is_achieved(self, context):
        return context.duration >= self.params['duration']


class CommentAchievement(Achievement):
    @property
    def title(self):
        if self.params['number'] == 1:
            return _("First comment made on SkyLines")
        return _("%(number)s comments made on SkyLines", **self.params)

    def is_achieved(self, context):
        # Assume SkyLinesAchievementDataCollector as context
        return context.comments_made >= self.params['number']


class TracksUploadedAchievement(Achievement):
    @property
    def title(self):
        if self.params['number'] == 1:
            return _("First track uploaded on SkyLines")
        return _("%(number)s tracks uploaded on SkyLines", **self.params)

    def is_achieved(self, context):
        # Assume SkyLinesAchievementDataCollector as context
        return context.tracks_uploaded >= self.params['number']


class UsersFollowedAchievement(Achievement):
    @property
    def title(self):
        if self.params['number'] == 1:
            return _("First user followed on SkyLines")
        return _("%(number)s users followed on SkyLines", **self.params)

    def is_achieved(self, context):
        # Assume SkyLinesAchievementDataCollector as context
        return context.users_followed >= self.params['number']


class FollowersAttractedAchievement(Achievement):
    @property
    def title(self):
        if self.params['number'] == 1:
            return _("Attracted first follower on SkyLines")
        return _("Attracted %(number)s followers on SkyLines", **self.params)

    def is_achieved(self, context):
        # Assume SkyLinesAchievementDataCollector as context
        return context.followers_attracted >= self.params['number']


FLIGHT_ACHIEVEMENTS = [TriangleAchievement('triangle-50', distance=50),
                       TriangleAchievement('triangle-100', distance=100),
                       TriangleAchievement('triangle-200', distance=200),
                       TriangleAchievement('triangle-300', distance=300),
                       TriangleAchievement('triangle-500', distance=500),
                       TriangleAchievement('triangle-1000', distance=1000),

                       DurationAchievement('duration-3', duration=3),
                       DurationAchievement('duration-5', duration=5),
                       DurationAchievement('duration-7', duration=7),
                       DurationAchievement('duration-10', duration=10),
                       DurationAchievement('duration-12', duration=12),
                       DurationAchievement('duration-15', duration=15),
                       ]


UPLOAD_ACHIEVEMENTS = [TracksUploadedAchievement('upload-1', number=1),
                       TracksUploadedAchievement('upload-10', number=10),
                       TracksUploadedAchievement('upload-100', number=100),
                       TracksUploadedAchievement('upload-1000', number=1000),
                       ]


COMMENT_ACHIEVEMENTS = [CommentAchievement('comment-1', number=1),
                        CommentAchievement('comment-10', number=10),
                        CommentAchievement('comment-100', number=100),
                        CommentAchievement('comment-1000', number=1000),
                        ]


FOLLOW_ACHIEVEMENTS = [UsersFollowedAchievement('follow-1', number=1),
                       UsersFollowedAchievement('follow-10', number=10),
                       UsersFollowedAchievement('follow-100', number=100),
                       UsersFollowedAchievement('follow-1000', number=1000),
                       ]


FOLLOWER_ACHIEVEMENTS = [FollowersAttractedAchievement('follower-1', number=1),
                         FollowersAttractedAchievement('follower-10', number=10),
                         FollowersAttractedAchievement('follower-100', number=100),
                         FollowersAttractedAchievement('follower-1000', number=1000),
                         ]


ACHIEVEMENT_BY_NAME = {a.name: a
                       for a in itertools.chain(FLIGHT_ACHIEVEMENTS,
                                                UPLOAD_ACHIEVEMENTS,
                                                COMMENT_ACHIEVEMENTS,
                                                FOLLOW_ACHIEVEMENTS,
                                                FOLLOWER_ACHIEVEMENTS)}


def get_achievement(name):
    return ACHIEVEMENT_BY_NAME[name]


def calculate_achievements(context, ach_definitions):
    return [a for a in ach_definitions if a.is_achieved(context)]


def get_user_achievements(user, ach_definitions):
    context = SkylinesAchievementDataCollector(user)
    return calculate_achievements(context, ach_definitions)


def get_flight_achievements(flight):
    context = FlightAchievementDataCollector(flight)
    return calculate_achievements(context, FLIGHT_ACHIEVEMENTS)
