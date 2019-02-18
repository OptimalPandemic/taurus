import numpy
import keras
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Dense, Dropout, Flatten
from machinelearning.DataLoader import DataLoader


batch_size = 108
num_tickers = 1  # Number of ticker symbols (i.e. BTC, ETH, etc.)
num_periods = 1  # Number of 30 minute periods in dataset

# Pull training data from data collection service
data_loader = DataLoader()
(v_lo_train, v_high_train, v_train), (v_lo_test, v_high_test, v_test) = data_loader.load_data()

model = Sequential()
model.add(Conv2D(2, kernel_size=(num_tickers, num_periods-2),
                 activation='relu',
                 input_shape=(3, num_tickers, num_periods)))
model.add(Dropout(0.25))
model.add(Conv2D(21, kernel_size=(num_tickers, 1), activation='relu'))
model.add(Dropout(0.5))
model.add(Flatten())
model.add(Conv2D(1, kernel_size=(num_tickers, 1), activation='relu'))
model.add(Dense(num_tickers+1, activation='softmax'))  # Single additional output is for cash bias

model.compile(loss=keras.losses.categorical_crossentropy,
              optimizer=keras.optimizers.Adam,
              metrics=['mae'])
