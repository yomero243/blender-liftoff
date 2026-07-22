bl_info = {
    "name": "Liftoff — Limpiar · Guardar · Renderizar",
    "author": "yomero243",
    "version": (1, 5, 0),
    "blender": (4, 2, 0),
    "location": "Vista 3D > Barra lateral > Pipeline  |  menú Archivo  |  Ctrl+Alt+S",
    "description": "Purga huérfanos, optimiza la escena, guarda, renderiza y sube copias listas para la nube (Colab).",
    "category": "Pipeline",
}

import bpy
import os
import glob
import string
import platform
import datetime
import subprocess

COLAB_URL = "https://colab.research.google.com/github/yomero243/blender-liftoff/blob/main/blender_render.ipynb"
DRIVE_URL = "https://drive.google.com/drive/my-drive"

# Nombres de carpeta raíz de Google Drive según el idioma del sistema
_DRIVE_ROOT_NAMES = (
    "My Drive", "Mi unidad", "Mon Drive", "Meine Ablage",
    "Il mio Drive", "Meu Drive", "O meu disco",
)


def _prefs():
    return bpy.context.preferences.addons[__name__].preferences


def _detect_drive_root():
    """Busca la raíz de Google Drive para escritorio en cualquier SO, letra de unidad o idioma."""
    home = os.path.expanduser("~")
    system = platform.system()
    candidates = []

    if system == "Windows":
        for letter in string.ascii_uppercase:
            root = f"{letter}:\\"
            if os.path.exists(root):
                candidates += [os.path.join(root, n) for n in _DRIVE_ROOT_NAMES]
        candidates += glob.glob(os.path.join(home, "*", "My Drive"))
    elif system == "Darwin":
        for base in glob.glob(os.path.join(home, "Library", "CloudStorage", "GoogleDrive-*")):
            candidates += [os.path.join(base, n) for n in _DRIVE_ROOT_NAMES]
        candidates.append(os.path.join(home, "Google Drive", "My Drive"))
        candidates.append("/Volumes/GoogleDrive/My Drive")
    else:  # Linux y otros
        candidates += [os.path.join(home, n) for n in ("GoogleDrive", "Google Drive")]

    for c in candidates:
        if os.path.isdir(c):
            return c
    return None


def _drive_folder():
    """Resuelve la ruta de la carpeta de sincronización con Google Drive."""
    path = _prefs().drive_folder.strip()
    if path:
        parent = os.path.dirname(path.rstrip("/\\")) or path
        if os.path.isdir(path) or os.path.isdir(parent):
            os.makedirs(path, exist_ok=True)
            return path
        return None

    root = _detect_drive_root()
    if root:
        folder = os.path.join(root, "RENDERS")
        os.makedirs(folder, exist_ok=True)
        return folder
    return None


def _get_renders_dir():
    """Devuelve la carpeta de salida para imágenes y animaciones."""
    out_dir = _drive_folder()
    if out_dir is None:
        base = os.path.dirname(bpy.data.filepath) if bpy.data.filepath else bpy.app.tempdir
        out_dir = os.path.join(base, "renders")
        os.makedirs(out_dir, exist_ok=True)
    return out_dir


def _open_folder(path):
    """Abre una carpeta en el explorador del sistema operativo."""
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    system = platform.system()
    if system == "Windows":
        os.startfile(path)
    elif system == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def _purge_orphans():
    """Purga recursivamente todos los datos huérfanos sin usuarios."""
    return bpy.data.orphans_purge(
        do_local_ids=True, do_linked_ids=True, do_recursive=True
    )


def _safe_name(name):
    """Genera un nombre de archivo seguro para Linux/Colab."""
    keep = "-_."
    cleaned = "".join(c if (c.isalnum() or c in keep) else "_" for c in name)
    return cleaned or "render"


def _show_dialog(message, title="Liftoff Pipeline", icon='INFO'):
    """Muestra un cuadro de diálogo emergente informativo en Blender."""
    def draw(self, context):
        for line in message.split("\n"):
            self.layout.label(text=line)
    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


class CSR_Preferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    drive_folder: bpy.props.StringProperty(
        name="Carpeta de Google Drive",
        description="Carpeta personalizada para guardar renders y copias de nube. "
                    "Déjalo vacío para autodetectar la carpeta 'RENDERS' en tu Google Drive.",
        subtype='DIR_PATH',
        default="",
    )

    auto_pack_textures: bpy.props.BoolProperty(
        name="Empaquetar texturas automáticamente al exportar",
        description="Empaqueta automáticamente imágenes y texturas dentro del .blend antes de subirlo a Drive",
        default=True,
    )

    compress_cloud_blend: bpy.props.BoolProperty(
        name="Comprimir copia de Drive",
        description="Comprime la copia .blend para acelerar la subida a la nube",
        default=True,
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "drive_folder")
        layout.prop(self, "auto_pack_textures")
        layout.prop(self, "compress_cloud_blend")
        
        resolved = _drive_folder()
        if resolved:
            layout.label(text="Carpeta detectada: " + resolved, icon='CHECKMARK')
        else:
            layout.label(text="No se encontró Google Drive - se usarán carpetas locales", icon='INFO')


class WM_OT_clean_save_render(bpy.types.Operator):
    """Purga datos huérfanos, guarda el archivo y renderiza a la carpeta de salida"""
    bl_idname = "wm.clean_save_render"
    bl_label = "Limpiar, Guardar y Renderizar"
    bl_options = {'REGISTER'}

    do_clean: bpy.props.BoolProperty(name="Limpiar (purgar huérfanos)", default=True)
    do_save: bpy.props.BoolProperty(name="Guardar", default=True)
    do_render: bpy.props.BoolProperty(name="Renderizar", default=True)
    render_anim: bpy.props.BoolProperty(name="Renderizar animación", default=False)

    def execute(self, context):
        scene = context.scene

        if self.do_clean:
            removed = _purge_orphans()
            self.report({'INFO'}, f"Limpieza: {removed} datablocks huérfanos purgados")

        if self.do_save:
            if not bpy.data.filepath:
                self.report({'ERROR'}, "El archivo nunca se ha guardado — usa 'Guardar como' primero")
                return {'CANCELLED'}
            bpy.ops.wm.save_mainfile()

        if self.do_render:
            if scene.camera is None:
                self.report({'ERROR'}, "No hay cámara activa en la escena")
                return {'CANCELLED'}

            blend_name = _safe_name(os.path.splitext(os.path.basename(bpy.data.filepath))[0] if bpy.data.filepath else "render")
            out_dir = _get_renders_dir()
            stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

            prev_path = scene.render.filepath
            if self.render_anim:
                scene.render.filepath = os.path.join(out_dir, f"{blend_name}_{stamp}_####")
            else:
                scene.render.filepath = os.path.join(out_dir, f"{blend_name}_{stamp}.png")

            try:
                if self.render_anim:
                    bpy.ops.render.render(animation=True)
                    self.report({'INFO'}, f"Animación renderizada en: {out_dir}")
                else:
                    bpy.ops.render.render(write_still=True)
                    self.report({'INFO'}, f"Render guardado: {scene.render.filepath}")
            finally:
                scene.render.filepath = prev_path

        return {'FINISHED'}


class WM_OT_preflight_check(bpy.types.Operator):
    """Diagnóstica la escena antes de enviar el archivo a la nube"""
    bl_idname = "wm.preflight_check"
    bl_label = "Chequeo Pre-Vuelo de la Escena"

    def execute(self, context):
        scene = context.scene
        issues = []

        if not bpy.data.filepath:
            issues.append("❌ El archivo no se ha guardado localmente aún.")
        elif bpy.data.is_dirty:
            issues.append("⚠️ El archivo tiene cambios no guardados.")
        else:
            issues.append("✅ Archivo guardado correctamente en disco.")

        if scene.camera is None:
            issues.append("❌ No hay cámara activa en la escena.")
        else:
            issues.append(f"✅ Cámara activa: '{scene.camera.name}'.")

        # Verificar datos huérfanos
        orphans = 0
        for collection in (bpy.data.meshes, bpy.data.materials, bpy.data.textures, bpy.data.images):
            for block in collection:
                if block.users == 0:
                    orphans += 1
        
        if orphans > 0:
            issues.append(f"⚠️ Hay {orphans} elementos huérfanos sin usar (pulsa 'Limpiar').")
        else:
            issues.append("✅ La escena está completamente limpia de huérfanos.")

        # Verificar texturas externas
        packed = sum(1 for img in bpy.data.images if img.packed_file)
        unpacked = sum(1 for img in bpy.data.images if img.filepath and not img.packed_file)
        issues.append(f"📦 Texturas: {packed} empaquetadas | {unpacked} externas.")

        report_msg = "\n".join(issues)
        _show_dialog(report_msg, title="Diagnóstico de Escena — Liftoff", icon='CHECKMARK' if orphans == 0 else 'INFO')
        return {'FINISHED'}


class WM_OT_open_renders_folder(bpy.types.Operator):
    """Abre la carpeta de renders en el explorador de archivos del sistema"""
    bl_idname = "wm.open_renders_folder"
    bl_label = "Abrir carpeta de renders"

    def execute(self, context):
        out_dir = _get_renders_dir()
        _open_folder(out_dir)
        self.report({'INFO'}, f"Carpeta abierta: {out_dir}")
        return {'FINISHED'}


class WM_OT_open_colab(bpy.types.Operator):
    """Abre el cuaderno Colab en tu navegador predeterminado"""
    bl_idname = "wm.open_colab"
    bl_label = "Ir a Google Colab"

    def execute(self, context):
        bpy.ops.wm.url_open(url=COLAB_URL)
        self.report({'INFO'}, "Notebook de Colab abierto en el navegador")
        return {'FINISHED'}


class WM_OT_upload_to_drive(bpy.types.Operator):
    """Empaqueta una copia autocontenida y la guarda en Google Drive para la nube"""
    bl_idname = "wm.upload_to_drive"
    bl_label = "Guardar copia en Drive"

    def execute(self, context):
        if not bpy.data.filepath:
            self.report({'ERROR'}, "Guarda el archivo principal primero (Guardar como)")
            return {'CANCELLED'}

        if bpy.data.is_dirty:
            bpy.ops.wm.save_mainfile()
            self.report({'INFO'}, "Archivo guardado antes de exportar")

        drive = _drive_folder()
        if drive is None:
            self.report({'ERROR'}, f"No se encontró la carpeta de Drive ({_prefs().drive_folder})")
            return {'CANCELLED'}

        prefs = _prefs()
        if prefs.auto_pack_textures:
            try:
                bpy.ops.file.pack_all()
                self.report({'INFO'}, "Texturas externas empaquetadas en la escena")
            except RuntimeError:
                pass

        blend_name = _safe_name(os.path.splitext(os.path.basename(bpy.data.filepath))[0])
        copy_path = os.path.join(drive, blend_name + "_cloud.blend")
        
        bpy.ops.wm.save_as_mainfile(
            filepath=copy_path,
            copy=True,
            compress=prefs.compress_cloud_blend
        )

        ver = f"{bpy.app.version[0]}.{bpy.app.version[1]}.{bpy.app.version[2]}"
        _show_dialog(
            f"¡Copia de nube guardada con éxito!\n\n📄 Archivo: {blend_name}_cloud.blend\n📂 Destino: {drive}\n📦 Blender {ver}",
            title="Copia para la Nube Guardada",
            icon='EXPORT'
        )
        return {'FINISHED'}


class VIEW3D_PT_clean_save_render(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Pipeline"
    bl_label = "Liftoff — Pipeline & Cloud Render"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # --- BOTÓN PRINCIPAL ALL-IN-ONE ---
        col = layout.column(align=True)
        col.scale_y = 1.4
        col.operator("wm.clean_save_render", text="Limpiar, Guardar y Render Frame", icon='RENDER_STILL')

        # --- CONTROLES RÁPIDOS DE ESCENA ---
        box_quick = layout.box()
        box_quick.label(text="Ajustes Rápidos de Render:", icon='PROPERTIES')
        
        row_eng = box_quick.row(align=True)
        row_eng.prop(scene.render, "engine", text="")
        row_eng.prop(scene.render, "resolution_percentage", text="Res %")

        if scene.render.engine == 'CYCLES':
            row_cyc = box_quick.row(align=True)
            row_cyc.prop(scene.cycles, "samples", text="Muestras")
            row_cyc.prop(scene.cycles, "use_denoising", text="Denoiser", icon='FILTER')

        # --- ACCIONES INDIVIDUALES ---
        box_actions = layout.box()
        box_actions.label(text="Acciones Rápidas:", icon='TOOL_SETTINGS')
        
        row1 = box_actions.row(align=True)
        op_c = row1.operator("wm.clean_save_render", text="Limpiar", icon='TRASH')
        op_c.do_clean, op_c.do_save, op_c.do_render = True, False, False
        
        op_s = row1.operator("wm.clean_save_render", text="Guardar", icon='FILE_TICK')
        op_s.do_clean, op_s.do_save, op_s.do_render = False, True, False

        row2 = box_actions.row(align=True)
        op_f = row2.operator("wm.clean_save_render", text="Render Frame", icon='RENDER_STILL')
        op_f.do_clean, op_f.do_save, op_f.do_render, op_f.render_anim = False, False, True, False

        op_a = row2.operator("wm.clean_save_render", text="Render Anim", icon='RENDER_ANIMATION')
        op_a.do_clean, op_a.do_save, op_a.do_render, op_a.render_anim = False, False, True, True

        box_actions.operator("wm.open_renders_folder", icon='FILE_FOLDER')

        # --- HERRAMIENTAS DE NUBE ---
        layout.separator()
        cloud = layout.box()
        cloud.label(text="Render en la Nube (Google Colab):", icon='WORLD')

        drive = _drive_folder()
        if drive:
            cloud.label(text="Drive: " + drive, icon='CHECKMARK')
        else:
            cloud.label(text="Drive no detectado — usando carpeta local", icon='INFO')

        c = cloud.column(align=True)
        c.scale_y = 1.2
        c.operator("wm.preflight_check", icon='DIAGNOSTICS')
        c.operator("wm.upload_to_drive", icon='EXPORT')
        c.operator("wm.open_colab", icon='URL')


def _menu_func(self, context):
    self.layout.separator()
    self.layout.operator("wm.clean_save_render", icon='RENDER_STILL')
    self.layout.operator("wm.upload_to_drive", icon='EXPORT')
    self.layout.operator("wm.preflight_check", icon='DIAGNOSTICS')
    self.layout.operator("wm.open_renders_folder", icon='FILE_FOLDER')
    self.layout.operator("wm.open_colab", icon='URL')


_classes = (
    CSR_Preferences,
    WM_OT_clean_save_render,
    WM_OT_preflight_check,
    WM_OT_open_renders_folder,
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
