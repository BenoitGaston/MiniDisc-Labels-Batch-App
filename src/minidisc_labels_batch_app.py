import streamlit as st

from  src.create_md_labels_batch import MiniDiscCovers

from pathlib import Path
import os
import shutil

import parameters as params

import zipfile
import io
import pandas as pd


UPLOAD_DIR = ".temp_md_labels_files"

def is_running_on_streamlit_cloud():
    # Check if "is_cloud" exists in secrets and is set to true
    running_on_cloud = st.secrets.get("general", {}).get("is_cloud", False)

    if running_on_cloud:
        pass
    else:
        st.warning("running on local")
    return running_on_cloud

def init_app():
    if "background_color" not in st.session_state:
        st.session_state.background_color ='navy_blue'
        if os.path.exists(UPLOAD_DIR):
            shutil.rmtree(UPLOAD_DIR)
        os.makedirs(UPLOAD_DIR)

    if "text_color" not in st.session_state:
        st.session_state.text_color ='gold'
    if "show_explanation_reload" not in st.session_state:
        st.session_state.show_explanation_reload = False
    if "reloaded_labels_csv" not in st.session_state:
        st.session_state.reloaded_labels_csv = None
    if "mini_disc_album_df" not in st.session_state:
        st.session_state.mini_disc_album_df = None
    if "uploaded_playlist" not in st.session_state:
        st.session_state.uploaded_playlist = None
    if "confirm_step" not in st.session_state:
        st.session_state.confirm_step = False
    if "missing_album_covers" not in st.session_state:
        st.session_state.missing_album_covers=[]


def reset_app():
    st.divider()
    if st.button("Reset App"):
        
        # Set confirmation step to True
        st.session_state["confirm_step"] = True

    if st.session_state["confirm_step"]:

        st.warning("Are you sure you want to perform this action?")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Confirm"):
                init_app()
                st.success("Action performed successfully!")
                st.session_state["confirm_step"] = False  # Reset confirmation step
                

        with col2:
            if st.button("Cancel"):
                st.info("Action canceled.")
                st.session_state["confirm_step"] = False  # Reset confirmation step
                




def on_show_explantion_click():
    st.session_state["show_explanation_reload"] = True


def colors_pick():
    
    if st.session_state.uploaded_playlist is not None:
        st.divider()


        color_method = st.segmented_control("How would you like to chose your colors", ['Black and White',
                                                                                        'Predefined Colors', 
                                                                                        'Hexadecimal','Reload a CSV File'],  default = 'Black and White')  
        if color_method=='Predefined Colors':

            col1, col2 = st.columns(2)
            with col1:
                st.session_state.background_color = st.segmented_control("Pick a background color",
                                                                         list(params.color_map.keys()) ,  default = 'black').replace('#','')
            with col2:
                st.session_state.text_color = st.segmented_control("Pick a text color",
                                                                   list(params.color_map.keys()) ,  default = 'white').replace('#','')
        elif color_method=='Hexadecimal':
            
            col1, col2 = st.columns(2)
            with col1:
                st.session_state.background_color = st.color_picker("Pick a background color (HEX format)", 
                                                                    "#0B0B2D").replace('#','')
            with col2:
                st.session_state.text_color = st.color_picker("Pick a text color (HEX format)", 
                                                              "#E2F3C5").replace('#','')
        elif color_method== 'Black and White':
            st.session_state.background_color = 'black'
            st.session_state.text_color = 'white'
        else: 
            
            st.session_state.background_color = 'black'
            st.session_state.text_color = 'white'
            st.write("""After reviewing the svg files created, you might find necessary to modify (in particular shorten/abbreviate) some Artist and Album names. 
                     You might also want to update the text and background colors label by label.
                    This can be done by 1. downloading the csv file created by the app (see below), 2. editing it, 3. reloading it to the app using this button.""")

            
                
            st.session_state.reloaded_labels_csv = st.file_uploader("Reload your modified `MiniDisc-Labels.csv` file", 
                                    accept_multiple_files=False, type=["csv"]) 
                
            if st.session_state.reloaded_labels_csv is not None:
                st.session_state.show_explanation_reload = False
            
                file_name ='MiniDisc-Labels.csv'
                save_path = Path(UPLOAD_DIR)/ file_name
                with open(save_path, "wb") as f:
                    f.write(st.session_state.reloaded_labels_csv.getbuffer())
                st.write(pd.read_csv(save_path)[['Display Album','Display Album Artist','background_color','text_color']])
 
            
def run_csv_creation():
    
    if st.session_state.uploaded_playlist is not None:
        st.divider()

        col1,col2,col3 = st.columns(3)
        with col1:
            pass
        with col2:
            if st.button("Create MiniDisc Labels Batch"):

            
                minidisc_covers = MiniDiscCovers(path_to_music_folder=UPLOAD_DIR)
                minidisc_covers.build_md_labels(st.session_state.background_color ,st.session_state.text_color)
                st.session_state.missing_album_covers = minidisc_covers.missing_covers
                st.session_state.mini_disc_album_df = minidisc_covers.mini_disc_album_df
                
        with col3:
            pass

        if st.session_state.mini_disc_album_df is not None:
            st.success("MiniDisc Labels created successfully")
        if len(st.session_state.missing_album_covers)>0:
                st.warning(f"""Some album cover where not found. You can use the `Upload album cover art image files` to upload them and run the app again.""")
                for album_missing in st.session_state.missing_album_covers:
                    st.warning(f"""
                            `{album_missing}` cover not found.
                            """)
                
    

def playlist_upload():

    st.session_state.uploaded_playlist = st.file_uploader("Choose an `.m3u8` playlist file", 
                                        accept_multiple_files=False, type=["m3u8"])
    if st.session_state.uploaded_playlist is not None:
        file_name ='MiniDisc.m3u8'
        save_path = os.path.join(UPLOAD_DIR, file_name)
        with open(save_path, "wb") as f:
                f.write(st.session_state.uploaded_playlist.getbuffer())


def album_covers_upload():

    if is_running_on_streamlit_cloud():
         
        album_cover_selection_options = ['Upload album cover art image files']
        album_cover_selection = st.segmented_control("Chose how to find album cover",
                                                    album_cover_selection_options, 
                                                    default = 'Upload album cover art image files')
    else:
        album_cover_selection_options = ['Search in my music library',
                                            'Upload album cover art image files']
        album_cover_selection = st.selectbox("Chose how to find album cover",album_cover_selection_options, index = 0)

    if album_cover_selection == 'Upload album cover art image files':
        st.write(f"To be used for the MiniDisc labels you cover files need to be named as:")
        st.write("`title_album`  or `title_album + artist` or  `title_album + artist` seperated by any special character.")
        st.write("and to  have one of the following extensions: `.jpg, .jpeg, .png`.")
        st.write("""Note that `artist`or `title_album` containing the characters `/`or `_` or `-` 
                 might not be found by the app or in the worst case cause some crashes.""")

        uploaded_covers = st.file_uploader("Upload cover arts files", 
                                    accept_multiple_files=True, type=["jpg", "jpeg", "png"])
        if uploaded_covers is not None:
            for file in uploaded_covers:
                file_name = file.name
                save_path = Path(UPLOAD_DIR)/ f'cover_{file_name.replace("/", "_").replace(":", "_")}'
                with open(save_path, "wb") as f:
                    f.write(file.getbuffer())

def download_ouputs():
    
    if st.session_state.mini_disc_album_df is not None:
        st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            
            #@st.cache_data
            def convert_df(df):
                # IMPORTANT: Cache the conversion to prevent computation on every rerun
                return df.to_csv(index=False).encode("utf-8")
            
            df_to_export = st.session_state.mini_disc_album_df.copy()
            csv = convert_df(df_to_export)
                
            st.download_button(
                        label="Download MiniDisc-Labels CSV file",
                        data=csv,
                        file_name="MiniDisc-Labels.csv",
                        mime="text/csv",
                    )

        with col2:

            files_path = [Path(UPLOAD_DIR)/file for file in os.listdir(Path(UPLOAD_DIR)) if file.endswith('.svg')]

            # Create a ZIP file in memory
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                for file_path in files_path:
                    # Add the file to the ZIP archive
                    arcname = os.path.basename(file_path)  # Use only the file name in the archive
                    zip_file.write(file_path, arcname=arcname)
            
            # Ensure the buffer is ready for reading
            zip_buffer.seek(0)

            # Provide a download button for the ZIP file
            st.download_button(
                label="Download ZIP",
                data=zip_buffer,
                file_name="MiniDisc_Labels.zip",
                mime="application/zip",
            )
        st.write("""You can download the `MiniDisc-Labels.csv` file, modify (in particular shorten/abbreviate) the values in the columns 
                 `Display Album`,`isplay Album Artist`,
                     `text_color` and `background_color`and reload the csv using the `Reload a CSV file` button above.""")
            
        st.write("""You can use custom text and background colors using any hexadecimal color or use one of the colors (as a string) in the list below.""")
        st.code("""'black','sky_blue','blue','blue_steel','blue_green',
                    'navy_blue','blue_turquoise','fushia','gold','green',
                    'pink','purple_light','purple','orange','red','yellow',
                    'white','silver'""")



def main():
    init_app()
    st.title("MiniDisc Labels Batch App")
    

    playlist_upload()

    if is_running_on_streamlit_cloud():
        st.warning("""Installing and running this app locally makes the following step optional. 
                 When running locally, the app is able to find the album cover arts directly inside your music library""")
        


    album_covers_upload()

    colors_pick()
    
    run_csv_creation()
    
    download_ouputs()
    






main()
