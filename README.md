# pygge

Python general graphic editor -- pygge (pro. 'piggie') -- is built on top of the python image library -- pillow/PIL 
-- to provide a scriptable graphics editor.

The core idea is that a canvas object can contain multiple components whose behaviour is controlled by code. The raw 
content for these components, be it an image file or text, is then interpreted by the component. This allows the 
programatic construction of template canvases which can be filled with content later, e.g. in a loop. 

The design goal is to facilitate rapid prototyping of game piece art for [tabletopia](www.tabletopia.com), but the
library should be generic and useful for many other tasks.