def draw(layout, obj_x, x_attr, obj_y, y_attr, obj_lock, lock_attr, x_label="X", y_label="Y", union_label="Size"):
    viewbool = getattr(obj_lock, lock_attr)

    row = layout.row(align=True)
    if viewbool:
        row.prop(obj_x, x_attr, text=union_label)
    else:
        row.prop(obj_x, x_attr, text=x_label)
        row.prop(obj_y, y_attr, text=y_label)
    row.prop(obj_lock, lock_attr, text="", icon="LOCKED" if viewbool else "UNLOCKED")