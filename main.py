import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.clock import Clock
import cv2
import pytesseract
from gtts import gTTS
import os
import numpy as np

# Setup Tesseract path (update for your system)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class SmartReaderApp(App):
    def build(self):
        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
            print("Error: Could not open webcam.")
            exit()
        
        self.img = Image(size_hint=(1, 0.8))
        self.status_label = Label(text="Press 'Capture' to take a picture.", size_hint=(1, 0.1))
        
        self.capture_button = Button(text="Capture", size_hint=(0.5, 0.1))
        self.capture_button.bind(on_press=self.capture_image)

        self.exit_button = Button(text="Exit", size_hint=(0.5, 0.1))
        self.exit_button.bind(on_press=self.exit_app)

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(self.img)
        layout.add_widget(self.status_label)
        layout.add_widget(self.capture_button)
        layout.add_widget(self.exit_button)
        
        Clock.schedule_interval(self.update_frame, 1.0 / 30.0)  # 30 FPS for webcam feed
        return layout

    def update_frame(self, dt):
        """ Capture the frame and convert it to a texture for display """
        ret, frame = self.camera.read()
        if ret:
            # Flip the frame vertically
            frame = cv2.flip(frame, 0)

            # Convert the frame to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Create a texture from the frame
            texture = kivy.graphics.texture.Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
            texture.blit_buffer(frame_rgb.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
            self.img.texture = texture

    def capture_image(self, instance):
        """ Capture image and run OCR to extract text """
        ret, frame = self.camera.read()
        if not ret:
            self.status_label.text = "Error capturing image."
            return
        
        img_path = 'captured_img.jpg'
        cv2.imwrite(img_path, frame)
        self.status_label.text = "Image captured. Processing text..."

        # Run OCR to extract text
        try:
            extracted_text = pytesseract.image_to_string(img_path)
        except Exception as e:
            self.status_label.text = f"Error during OCR: {e}"
            return

        # Check if text was detected
        if extracted_text.strip():
            self.status_label.text = f"Extracted Text: {extracted_text}"
            tts = gTTS(text=extracted_text, lang='en')
            audio_path = "extracted_text.mp3"
            tts.save(audio_path)
            os.system(f"start {audio_path}")  # Change command for non-Windows OS
        else:
            self.status_label.text = "No text detected."
            tts = gTTS(text="No text detected in the image.", lang='en')
            audio_path = "no_text_detected.mp3"
            tts.save(audio_path)
            os.system(f"start {audio_path}")  # Change command for non-Windows OS

        # Clean up
        os.remove(img_path)

    def exit_app(self, instance):
        """ Close the app """
        self.camera.release()
        cv2.destroyAllWindows()
        App.get_running_app().stop()

if __name__ == '__main__':
    SmartReaderApp().run()
