# IceToolbag
A blender addon for VSE

Like its name, this toolbag should contain lots of things.

## Notice

**This addon is still in develop, pretty unstable. So i leave it as alpha version right now.**

## Features

- Marker

| Feature         | Description                                                  | Demo                |
| --------------- | ------------------------------------------------------------ | ------------------- |
| Batch rename    | rename all marker(`%d` represent the index of marker).       | ![](doc/marker.gif) |
| Marker Layer    | now marker has layer too. you can switch to another layer or rename this marker layer. | ![](doc/switch.gif) |
| Align to marker | Align a strip to marker                                      |                     |
| Beat match      | input two marker layers with the corresponding markers of movie and audio, this operation will match them using `speed` strip. |                     |

- Effects

| Features            | Description                                                  | Demo               |
| ------------------- | ------------------------------------------------------------ | ------------------ |
| Convert 2 RichStrip | Before adding effects to a strip, you need to select a movie and an audio strip or just one movie strip to convert. | ![](doc/c2rs.gif)  |
| Original Effect     | This effect represents the original strip which cannot be created manually but has lots of control like transformation and rotation. | ![](doc/ori.gif)   |
| FastBlur Effect     | Blender has Gaussian blur but pretty slow and not perfect when we want a blur background. This effect does a trick to blur the background. | ![](doc/fblur.gif) |
| Ramp Effect         | Like ramp node in nuke but less control. **Still has some bugs about the formulation.** | ![](doc/ramp.gif)  |
|  Copy Effect   | Must select an effect you want to copy before adding this effect. | ![](doc/copy.gif) |
| Matte Effect        | Simple matte effect. **Still in progress.**                  | ![](doc/matte.gif) |
| Pixelize Effect     | Mosaic effect.                                               | ![](doc/other.gif) |
| Blender Internal Effect | So it's familiar with you. I'm not going to introduce them.  |                    |

## TODO

- support move up and down the effect

- blender limits the number of channels maybe we will run out of it

- add more effects

- effects should has clip property and can interactive in viewport.

## Known Issues

- copy the richstrip would break the addon because blender rename all the strips
- when drag the value, it seems blender cost lots of memory.
- cannot insert key frame for some (most) properties

## Last things...

I'm sorry for my poor English in document. Feel free to open an issue if you have any question.