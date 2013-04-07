theobot
=======

Functions running on [[User:Theo's Little Bot]] on enwiki ([userpage](//en.wikipedia.org/wiki/User:Theo's Little Bot))

Index
----
*Last updated 7 April 2013*
* **NonFreeImageResizer** - reduces size of non-free images on Wikipedia
 * *resizer_auto.py* - Base script for resizer
 * *little_image.py* - Sub-module of resizer_auto.py that actually does the resizing
* **MissingDescriptionNotifier** - notifies users who have uploaded images without descriptions
 * *desc_notifier.py* - Base script for search and notifications
* **FileTagger** - Tags files that are embedded on pages in a given category wih WikiProject banners
 * *file_tagger.py* - Base script for finding files in need of tag and tagging them
* **AustraliaRoads** - Adds |road and |road-importance to a given subset of Australia-related articles
 * *australia_roads.py* - Recursively finds and tags articles
* **MiscTasks** - A variety of simple tasks
 * *rileybot_global_watchlist.py* - Updates [[User:RileyBot]]'s global watchlist

Prerequisties
----
* [mwclient](http://sourceforge.net/projects/mwclient/)
* [mwparserfromhell](https://github.com/earwig/mwparserfromhell)
* [PIL](http://www.pythonware.com/products/pil/) (NonFreeImageResizer only)
