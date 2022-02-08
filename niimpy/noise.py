
#Ambient Noise
def ambient_noise(noise, subject, begin=None, end=None):
    """ Returns a Dataframe with 5 possible computations regarding the noise
    ambient plug-in: average decibels, average frequency, number of times when
    there was noise in the day, number of times when there was a loud noise in
    the day (>70dB), and number of times when the noise matched the speech noise
    level and frequency (65Hz < freq < 255Hz and dB>50 )



    NOTE: This function aggregates data by day.

    Parameters
    ----------
    noise: DataFrame with subject data (or database for backwards compatibility)
    subject: string, optional (backwards compatibility only, in the future do filtering before).
    begin: datetime, optional
    end: datetime, optional


    Returns
    -------
    avg_noise: Dataframe

    """
    # TODO: move to niimpy.noise
    # TODO: add arguments for frequency/decibels/silence columns
    # Backwards compatibilty if a database was passed
    if isinstance(noise, niimpy.database.Data1):
        noise = noise.raw(table='AwareAmbientNoise', user=subject)
    # Maintain backwards compatibility in the case subject was passed and
    # questions was *not* a dataframe.
    elif isinstance(subject, string):
        noise = noise[noise['user'] == subject]

    # Shrink the dataframe down to only what we need
    noise = noise[['double_frequency', 'is_silent', 'double_decibels', 'datetime']]

    # Extract the data range (In the future should be done before this function
    # is called.)
    if begin is not None or end is not None:
        noise = date_range(noise, begin, end)

    noise['is_silent']=pd.to_numeric(noise['is_silent'])

    loud = noise[noise.double_decibels>70] #check if environment was noisy
    speech = noise[noise['double_frequency'].between(65, 255)]
    speech = speech[speech.is_silent==0] #check if there was a conversation
    silent=noise[noise.is_silent==0] #This is more what moments there are noise in the environment.
    avg_noise=noise.resample('D', on='datetime').mean() #average noise
    avg_noise=avg_noise.drop(['is_silent'],axis=1)

    if not silent.empty:
        silent=silent.resample('D', on='datetime').count()
        silent = silent.drop(['double_decibels','double_frequency','datetime'],axis=1)
        silent=silent.rename(columns={'is_silent':'noise'})
        avg_noise = avg_noise.merge(silent, how='outer', left_index=True, right_index=True)

    if not loud.empty:
        loud=loud.resample('D', on='datetime').count()
        loud = loud.drop(['double_decibels','double_frequency','datetime'],axis=1)
        loud=loud.rename(columns={'is_silent':'loud'})
        avg_noise = avg_noise.merge(loud, how='outer', left_index=True, right_index=True)

    if not speech.empty:
        speech=speech.resample('D', on='datetime').count()
        speech = speech.drop(['double_decibels','double_frequency','datetime'],axis=1)
        speech=speech.rename(columns={'is_silent':'speech'})
        avg_noise = avg_noise.merge(speech, how='outer', left_index=True, right_index=True)

    return avg_noise
