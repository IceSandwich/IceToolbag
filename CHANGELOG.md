## 0.0.1 alpha

1. support keyframes animation for most properties.
2. get rid of copy effect since we can duplicate richstrip.
3. update some api of base effect class, so everyone can write his own effect.
4. support blender 2.9


## 0.0.2 alpha

1. gallery strip achieved.
2. fix some bugs and add document for some class source code.
3. add shadow effects and mirror effect.
4. richstrip can be mixed with gallery strip.
5. simplify some apis.

## 0.0.3 alpha

1. support move up and down effects
2. add mask box for some effects
3. add export box for animation of properties
4. fix issue for fastblur and pixelize
5. control enable/disable effect
6. support blender 3.0

## 0.0.6 alpha

1. UI improvement.
2. Add `freeze frame` operator.
3. Delete unnecessary speed strip to improve efficiency.
4. Beat match for blender 3.0.
5. Some api changed. Effects can use handler/signals in some way. Effects can report errors while creating.
6. Add effect widgets. `Crop box` to crop some area. Add `through`  option to some effects.
7. Fix bugs in `FastBlur` and `gmic` effect. `GMIC` effect becomes more robust.
8. Improve g'mic usage. Set filepath in preference window.
9. Effects autoloader. Programmer haven't to setup effects in `ICETB_EFFECTS_CLASSES`.
10. `Copy`effect returns but make some limitations to fit the system.

