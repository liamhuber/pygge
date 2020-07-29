# pygge

![Travis build status](https://travis-ci.com/github/liamhuber/pygge/pygge.svg?branch=master)

The overly-ambitiously-named Python general graphic editor -- pygge (pro. 'piggie') -- is built on top of the python 
image library -- pillow/PIL -- to provide a scriptable graphics editor.

The core idea is to allow what-you-type-is-what-you-get graphics editing in the python environment. To this end, there 
is a canvas object which can contain multiple components whose behaviour is controlled by code. The raw content for 
these components, be it an image file or text, is then interpreted by the component. This allows the programatic 
construction of template canvases which can be filled with content later, e.g. in a loop. 

In practice, this project was motivated by a need to rapidly prototype game piece art for the 
[tabletopia](www.tabletopia.com) platform, but the library should in principle be generic and useful for other tasks.