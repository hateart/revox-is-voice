import boto3
import pydub
import uuid
import os
import torch
from pydub import AudioSegment
from funasr import AutoModel
import soundfile
import torchaudio
import numpy as np

#CHECK_FILE = 'audios/986931/2508179_7848d64c-3b53-51d2-fdd2-d115b8cd9e68.mp3'
#CHECK_FILE = 'audios/25/3578100_bfa63af9-f37c-1746-ccaa-21ec327fb6d4.mp3' #empty
CHECK_FILE = 'audios/308265/3656735_9a054a46-05f1-bf0b-fc74-0da8c3a7e4b3.mp3'
DATA_STORAGE = '/app'


class _ML_Service:

    _instance = None
    _model = None
    _s3 = None

    def __init__(self):
        print("Initialize the new instance")
        self._s3 = boto3.client('s3',
                          region_name="eu-central-1",
                          aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                          aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))
        self._model = AutoModel(model="fsmn-vad", model_revision="v2.0.4")

    def predict(self, file_key):
        values = self._fetch_file(file_key, DATA_STORAGE, uuid.uuid4())
        return values

    def _fetch_file(self, file_key, local_storage_path, uid):

        uid = uuid.uuid4()

        local_file_path = os.path.join(local_storage_path, f'{uid}.mp3')
        # Fetch the file from S3 and save it locally
        try:
            self._s3.download_file('vi-st', file_key, local_file_path)
            #print(f"File downloaded successfully: {file_key} -> {local_file_path}")
        except Exception as e:
            raise ValueError(f"Error downloading file: {file_key} {e}")

        audio = AudioSegment.from_mp3(local_file_path)
        sample_rate = 16000
        audio = audio.set_frame_rate(sample_rate)
        wav_file = local_storage_path + str(uid) + '.wav'

        audio.export(wav_file, format="wav")
        res = self._model.generate(input=wav_file)

        waveform, sample_rate = torchaudio.load(wav_file)
        intervals_samples = np.array(res[0]['value'])* (sample_rate / 1000)
        # Extract segments from the audio file based on the time intervals
        segments = []
        for start_sample, end_sample in intervals_samples:
            segment = waveform[:, int(start_sample):int(end_sample)]
            segments.append(segment)


        # Calculate the number of samples in waveform
        number_of_samples_original = waveform.size(1)

        # Calculate the duration in seconds
        duration_seconds_original = number_of_samples_original / sample_rate

        if not segments:
            data = {
                "duration_seconds_original": duration_seconds_original,
                "duration_seconds": 0,
                "percentage": 0
            }

            return data

        # Concatenate the segments along the time axis
        concatenated_segments = torch.cat(segments, dim=1)

        # Calculate the number of samples in concatenated_segments
        number_of_samples = concatenated_segments.size(1)

        # Calculate the duration in seconds
        duration_seconds = number_of_samples / sample_rate


        # Calculate the percentage
        percentage = (duration_seconds / duration_seconds_original) * 100
        percentage = round(percentage, 2)

        try:
            os.remove(local_file_path)
            os.remove(wav_file)
        except Exception as e:
            # Handle other exceptions
            print(f"An error occurred: {e}")

        data = {
            "duration_seconds_original": duration_seconds_original,
            "duration_seconds": duration_seconds,
            "percentage": percentage
        }

        return data

def ML_Service():

    # only one insctance we need
    if _ML_Service._instance is None:
        _ML_Service._instance = _ML_Service()
    return _ML_Service._instance

if __name__ == "__main__":

    print("Hello!")

    access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')

    print(f"AWS Access Key ID: {access_key}")
    print(f"AWS Secret Access Key: {secret_key}")

    service = ML_Service()

    result = service.predict(CHECK_FILE)
    print(result)