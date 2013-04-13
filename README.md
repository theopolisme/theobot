theobot
=======

Functions running on [[User:Theo's Little Bot]] on enwiki ([userpage](//en.wikipedia.org/wiki/User:Theo's Little Bot))

Index
----
 * *NonFreeImageResizer* - reduces size of non-free images on Wikipedia
  * *resizer_auto.py* - Base script for resizer
  * *little_image.py* - Sub-module of resizer_auto.py that actually does the resizing
 * *rileybot_global_watchlist.py* - Updates [[User:RileyBot]]'s global watchlist
 * *desc_notifier.py* - notifies users who have uploaded images without descriptions
 * *file_tagger.py* - Tags files that are embedded on pages in a given category wih WikiProject banners
 * *australia_roads.py* - Adds |road and |road-importance to a given subset of Australia-related articles
 * *reggaeton_tagger.py* - Tags reggaeton-related pages with |reggaeton=yes
 * *classical_tagger.py* - Updates importance values for certain Roman/Grecian articles

Prerequisties
----
* [mwclient](http://sourceforge.net/projects/mwclient/)
* [mwparserfromhell](https://github.com/earwig/mwparserfromhell)
* [PIL](http://www.pythonware.com/products/pil/) (NonFreeImageResizer only)
