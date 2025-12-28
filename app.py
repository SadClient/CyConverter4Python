import streamlit as st
import subprocess
import os
import tempfile

st.set_page_config(page_title="CyConverter4Python 🚀", layout="wide")

st.title("🚀 CyConverter4Python")
st.markdown("### Python kodunu profesyonel **Windows .exe**'ye çevir — saniyeler içinde, tarayıcıdan!")

# Opsiyonel özellikler
col1, col2, col3 = st.columns(3)
with col1:
    author = st.text_input("Yazar Adı (opsiyonel)", placeholder="Adın veya şirketin")
with col2:
    icon_file = st.file_uploader("Özel İkon (.ico - opsiyonel)", type=["ico"])
with col3:
    requirements_file = st.file_uploader(
        "requirements.txt (opsiyonel)",
        type=["txt"],
        help="requests, tkinter, pygame, pandas, selenium gibi paketler kullanıyorsan yükle"
    )

# Kod girişi
option = st.radio("Python kodunu nasıl eklemek istersin?", ("Dosya Yükle 📁", "Elle Yaz ✍️"), horizontal=True)

code = None
filename = "myapp"

if option == "Dosya Yükle 📁":
    uploaded_file = st.file_uploader("Ana Python dosyanı yükle (.py)", type=["py"])
    if uploaded_file is not None:
        filename = os.path.splitext(uploaded_file.name)[0]
        code = uploaded_file.getvalue().decode("utf-8")
        st.success(f"✅ Dosya yüklendi: **{uploaded_file.name}**")
        st.code(code, language="python")
else:
    code = st.text_area(
        "Kodunu buraya yaz veya yapıştır",
        value='# Merhaba!\nprint("CyConverter4Python ile EXE oldum! 🚀")\n# requirements.txt ile istediğin paketi ekleyebilirsin',
        height=400
    )

if code is None:
    st.info("👆 Lütfen bir .py dosyası yükle veya kod yaz.")
    st.stop()

if st.button("🚀 EXE Oluştur & İndir", type="primary", use_container_width=True):
    with st.spinner("EXE oluşturuluyor... 20-60 saniye sürebilir 🔨"):
        with tempfile.TemporaryDirectory() as temp_dir:
            source_path = os.path.join(temp_dir, f"{filename}.py")
            with open(source_path, "w", encoding="utf-8") as f:
                f.write(code)

            final_author = author.strip() or "CyConverter4Python User"
            description = "CyConverter4Python ile oluşturuldu"
            copyright_text = f"© 2025 {final_author}"

            # requirements.txt varsa kur
            if requirements_file:
                req_path = os.path.join(temp_dir, "requirements.txt")
                with open(req_path, "wb") as f:
                    f.write(requirements_file.getvalue())
                st.info("📦 Paketler yükleniyor...")
                install_result = subprocess.run(["pip", "install", "-r", req_path], capture_output=True, text=True, timeout=180)
                if install_result.returncode != 0:
                    st.error("Bazı paketler yüklenemedi:")
                    st.code(install_result.stderr)
                    st.stop()
                st.success("✅ Tüm paketler yüklendi!")

            # PyInstaller komutu
            pyi_args = [
                "pyinstaller", "--onefile", "--noconsole",
                "--name", filename,
                "--distpath", temp_dir,
                source_path
            ]

            # İkon ekle
            if icon_file:
                icon_path = os.path.join(temp_dir, "icon.ico")
                with open(icon_path, "wb") as f:
                    f.write(icon_file.getvalue())
                pyi_args += ["--icon", icon_path]

            # Metadata ekle
            version_file = os.path.join(temp_dir, "version_info.txt")
            version_content = f'''# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(filevers=(1,0,0,0), prodvers=(1,0,0,0)),
  kids=[
    StringFileInfo([
      StringTable(u'040904B0', [
        StringStruct(u'CompanyName', u'{final_author}'),
        StringStruct(u'FileDescription', u'{description}'),
        StringStruct(u'LegalCopyright', u'{copyright_text}'),
        StringStruct(u'ProductName', u'{filename}'),
        StringStruct(u'OriginalFilename', u'{filename}.exe')
      ])
    ]),
    VarFileInfo([VarStruct(u'Translation', [1033,1200])])
  ]
)'''
            with open(version_file, "w", encoding="utf-8") as f:
                f.write(version_content)
            pyi_args += ["--version-file", version_file]

            result = subprocess.run(pyi_args, capture_output=True, text=True, timeout=300)
            exe_path = os.path.join(temp_dir, f"{filename}.exe")

            if os.path.exists(exe_path):
                with open(exe_path, "rb") as f:
                    exe_data = f.read()
                st.success("✅ EXE başarıyla oluşturuldu!")
                st.markdown(f"**Dosya adı:** `{filename}.exe` | **Yazar:** `{final_author}`")
                if requirements_file:
                    st.info("📦 Tüm paketlerin EXE içinde!")
                st.download_button(
                    "📥 EXE Dosyasını İndir",
                    exe_data,
                    file_name=f"{filename}.exe",
                    mime="application/octet-stream",
                    type="primary",
                    use_container_width=True
                )
                st.balloons()
            else:
                st.error("❌ Oluşturma hatası")
                st.code(result.stderr or "Bilinmeyen hata")

st.caption("Made with ❤️ by Sad_Always — An AlexisHQ project | Python → Professional EXE")
