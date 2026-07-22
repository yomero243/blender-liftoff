bl_info = {
    "name": "Clean, Save & Render",
    "author": "Claude",
    "version": (1, 2, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Pipeline  |  File menu  |  Ctrl+Alt+S",
    "description": "Purge orphans, save, render to your Google Drive folder, and push a cloud-ready copy for Colab.",
    "category": "Pipeline",
}

import bpy
import os
import datetime

COLAB_URL = "https://colab.research.google.com/github/ynshung/blender-colab/blob/master/blender_render.ipynb"
DRIVE_URL = "https://drive.google.com/drive/my-drive"
DEFAULT_DRIVE_FOLDER = r"G:\Mi unidad\RENDERS"


def _prefs():
    return bpy.context.preferences.addons[__name__].preferences


def _drive_folder():
    """Return the configured Drive folder if it exists, else None."""
    path = _prefs().drive_folder
    if path and os.path.isdir(os.path.dirname(path) or path):
        os.makedirs(path, exist_ok=True)
        return path
    return None


def _purge_orphans():
    return bpy.data.orphans_purge(
        do_local_ids=True, do_linked_ids=True, do_recursive=True
    )


class CSR_Preferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    drive_folder: bpy.props.StringProperty(
        name="Google Drive folder",
        description="Synced Google Drive Desktop folder. Renders and the cloud .blend copy are saved here so Drive uploads them automatically.",
        subtype='DIR_PATH',
        default=DEFAULT_DRIVE_FOLDER,
    )

    def draw(self, context):
        self.layout.prop(self, "drive_folder")


class WM_OT_clean_save_render(bpy.types.Operator):
    """Purge orphan data, save the file, then render the current frame to the Drive folder"""
    bl_idname = "wm.clean_save_render"
    bl_label = "Clean, Save & Render"
    bl_options = {'REGISTER'}

    do_clean: bpy.props.BoolProperty(name="Clean (purge orphans)", default=True)
    do_save: bpy.props.BoolProperty(name="Save", default=True)
    do_render: bpy.props.BoolProperty(name="Render", default=True)

    def execute(self, context):
        scene = context.scene

        if self.do_clean:
            removed = _purge_orphans()
            self.report({'INFO'}, f"Cleaned: purged {removed} orphan datablocks")

        if self.do_save:
            if not bpy.data.filepath:
                self.report({'ERROR'}, "File was never saved - use 'Save As' first")
                return {'CANCELLED'}
            bpy.ops.wm.save_mainfile()

        if self.do_render:
            if scene.camera is None:
                self.report({'ERROR'}, "No active camera in the scene")
                return {'CANCELLED'}

            blend_name = os.path.splitext(os.path.basename(bpy.data.filepath))[0] or "render"
            # prefer the Drive folder; fall back to a local /renders folder
            out_dir = _drive_folder()
            if out_dir is None:
                base = os.path.dirname(bpy.data.filepath) or bpy.app.tempdir
                out_dir = os.path.join(base, "renders")
                os.makedirs(out_dir, exist_ok=True)
            stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

            prev_path = scene.render.filepath
            scene.render.filepath = os.path.join(out_dir, f"{blend_name}_{stamp}.png")
            try:
                bpy.ops.render.render(write_still=True)
                self.report({'INFO'}, f"Rendered -> {scene.render.filepath}")
            finally:
                scene.render.filepath = prev_path

        return {'FINISHED'}


class WM_OT_open_colab(bpy.types.Operator):
    """Open the blender-colab render notebook in your web browser"""
    bl_idname = "wm.open_colab"
    bl_label = "Go to Colab"

    def execute(self, context):
        bpy.ops.wm.url_open(url=COLAB_URL)
        self.report({'INFO'}, "Opened blender-colab notebook in browser")
        return {'FINISHED'}


class WM_OT_upload_to_drive(bpy.types.Operator):
    """Pack a cloud-ready copy and save it into your Google Drive folder,
    which Drive Desktop then uploads automatically."""
    bl_idname = "wm.upload_to_drive"
    bl_label = "Save copy to Drive"

    def execute(self, context):
        if not bpy.data.filepath:
            self.report({'ERROR'}, "Save the file first (Save As)")
            return {'CANCELLED'}

        drive = _drive_folder()
        if drive is None:
            self.report({'ERROR'},
                        f"Drive folder not found: {_prefs().drive_folder}  (set it in Add-on Preferences)")
            return {'CANCELLED'}

        # pack all external textures so the cloud copy is self-contained
        try:
            bpy.ops.file.pack_all()
        except RuntimeError:
            pass

        blend_name = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
        copy_path = os.path.join(drive, blend_name + "_cloud.blend")
        bpy.ops.wm.save_as_mainfile(filepath=copy_path, copy=True, compress=True)

        self.report({'INFO'}, f"Saved to Drive (auto-uploading): {copy_path}")
        return {'FINISHED'}


class VIEW3D_PT_clean_save_render(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Pipeline"
    bl_label = "Clean · Save · Render"

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.scale_y = 1.4
        col.operator("wm.clean_save_render", icon='RENDER_STILL')

        box = layout.box()
        box.label(text="Individual steps:", icon='TOOL_SETTINGS')
        row = box.row(align=True)
        op = row.operator("wm.clean_save_render", text="Clean", icon='TRASH')
        op.do_clean, op.do_save, op.do_render = True, False, False
        op = row.operator("wm.clean_save_render", text="Save", icon='FILE_TICK')
        op.do_clean, op.do_save, op.do_render = False, True, False
        op = row.operator("wm.clean_save_render", text="Render", icon='RENDER_STILL')
        op.do_clean, op.do_save, op.do_render = False, False, True

        layout.separator()
        cloud = layout.box()
        cloud.label(text="Cloud render (Colab):", icon='WORLD')
        drive = _drive_folder()
        cloud.label(text=("Drive: " + (_prefs().drive_folder if drive else "NOT FOUND")),
                    icon='CHECKMARK' if drive else 'ERROR')
        c = cloud.column(align=True)
        c.scale_y = 1.2
        c.operator("wm.upload_to_drive", icon='EXPORT')
        c.operator("wm.open_colab", icon='URL')


def _menu_func(self, context):
    self.layout.separator()
    self.layout.operator("wm.clean_save_render", icon='RENDER_STILL')
    self.layout.operator("wm.upload_to_drive", icon='EXPORT')
    self.layout.operator("wm.open_colab", icon='URL')


_classes = (
    CSR_Preferences,
    WM_OT_clean_save_render,
    WM_OT_open_colab,
    WM_OT_upload_to_drive,
    VIEW3D_PT_clean_save_render,
)

_addon_keymaps = []


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_file.append(_menu_func)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='Window', space_type='EMPTY')
        kmi = km.keymap_items.new(
            "wm.clean_save_render", type='S', value='PRESS', ctrl=True, alt=True
        )
        _addon_keymaps.append((km, kmi))


def unregister():
    for km, kmi in _addon_keymaps:
        km.keymap_items.remove(kmi)
    _addon_keymaps.clear()

    bpy.types.TOPBAR_MT_file.remove(_menu_func)
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
