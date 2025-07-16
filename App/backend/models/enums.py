from enum import Enum

class WatchlistStatusEnum(str, Enum):
    watching = 'watching'
    completed = 'completed'
    planned = 'planned'
    dropped = 'dropped'

class TrailerTypeEnum(str, Enum):
    Trailer = 'Trailer'
    Teaser = 'Teaser'
    Clip = 'Clip'
    Featurette = 'Featurette'
    BehindTheScenes = 'Behind the Scenes'
    Bloopers = 'Bloopers'
    OpeningScene = 'Opening Scene'
    EndingScene = 'Ending Scene'
    DeletedScene = 'Deleted Scene'

class SiteEnum(str, Enum):
    YouTube = 'YouTube'
    Vimeo = 'Vimeo'

class EventTypeEnum(str, Enum):
    click = 'click'
    view = 'view'
    like = 'like'
    share = 'share'
    comment = 'comment'
    watch = 'watch'
