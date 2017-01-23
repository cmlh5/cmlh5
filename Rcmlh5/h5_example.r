# -------------------------------------------------
# Manipulate CMLh5 files
# by Martin Fencl
# e-mail: martin.fencl@cvut.cz
# -------------------------------------------------

# Example implementation of h5 package (version 0.9.8) for manipulating files
# in CMLh5 data format. For details or other low level functions see
# documentation to h5 package. 

# -------------------------------------------------

library(h5)

# Generate CML sample data  ----------------------------------------------------

Sys.setenv(tz="UTC")  # set system timezone to UTC

ch1 <- data.frame("time"= as.POSIXct(seq(0, by=60, length=20),
                                     origin="2017-01-01"),
                   "rx" = round(rnorm(20, 100, 1)/3, 1),
                   "tx" = round(rnorm(20, 8, .5), 0))

ch2 <- data.frame("time"= as.POSIXct(seq(0, by=60, length=20),
                                     origin="2017-01-01"),
                  "rx" = round(rnorm(20, 100, 1)/3, 1),
                  "tx" = round(rnorm(20, 8, .5), 0))




# Create cmlh5 file ------------------------------------------------------------

# 1. Create/Open file 'test.h5' (mode set to append) ---
file <- h5file("cmlh5_Rtest.h5", mode = 'a')


# 2. Create groups, subgroups and dataset ---
file["cml_1/channel_1/time"] <- as.numeric(ch1$time)
file["cml_1/channel_1/rx"] <- ch1$rx
# additional DataSet arguments can be passed as follows (see ?createDataSet)
file["cml_1/channel_1/tx", chunksize = 100, compression = 8] <- ch1$tx

# Alternatively, dataset can be defined using createDataSet function 
createDataSet(file["/cml_1/channel_2/"], datasetname = "time",
              data = as.numeric(ch2$time))
createDataSet(file["/cml_1/channel_2/"], datasetname = "rx", data = ch2$rx)
createDataSet(file["/cml_1/channel_2/"], datasetname = "tx", data = ch2$tx,
              chunksize = 100, compression = 8)


# 3. Store metadata (as attributes) ---

# 3a. Store metadata at the root level (as attributes)
h5attr(file, "file_format") <- "CMLh5" #This must always be set to ‘CMLh5
h5attr(file, "file_format_version") <- "0.0" 
h5attr(file, "author_name") <- "Martin Fencl" #optional
h5attr(file, "author_email") <- "martin.fencl@cvut.cz" #optional
h5attr(file, "additional_info") <- "Example file" #additional

# 3b. Store metadata at CML level (as attributes)
group <- file["/cml_1"]
h5attr(group,"site_a_longitude") <- 13.5248 
h5attr(group,"site_b_latitude") <- 51.1540
h5attr(group,"site_b_longitude") <- 13.5112 
h5attr(group,"site_b_altitude") <- 51.1427
h5attr(group,"cml_id") <- "56_57"
h5close(group)

# 3c. Store metadata at channel level (as attributes)
group <- file["/cml_1/channel_1"]
h5attr(group,"frequency") <- 37.62
h5attr(group,"polarization") <- "V" 
h5attr(group,"channel_id") <- "57" 
h5attr(group,"atpc") <- "on"
h5close(group)

group <- file["/cml_1/channel_2"]
h5attr(group,"frequency") <- 38.88
h5attr(group,"polarization") <- "V" 
h5attr(group,"channel_id") <- "58" 
h5attr(group,"atpc") <- "on"
h5close(group)

# 3d. Store metadata at array (dataset) level (as attributes)

dset.loc <- c("cml_1/channel_1/time", "cml_1/channel_1/rx",
              "cml_1/channel_1/tx", "cml_1/channel_2/time",
              "cml_1/channel_2/rx", "cml_1/channel_2/tx")
dset.quant <- c("time","tx","rx","time","tx","rx")
dset.unit <- c("POSIX time","dBm","dBm","POSIX time","dBm","dBm")

for (i in 1:6){
    dset <- file[dset.loc[i]]
    h5attr(dset, "quantity") <-  dset.quant[i]
    h5attr(dset, "unit") <-  dset.unit[i]
    h5close(dset)  # closing each dataset object
}    


# 4. Close file ---
# Closing only file will not close all lower level connections. Thus, it is
# better to close the objects just after manipulating. Note also that
# removing or rewriting the variables (e.g. rm(group) or group <- "blablabla")
# will not close the connection.

h5close(file) 




# Read cmlh5 file --------------------------------------------------------------


# 1. open file in a reading mode ---
file <- h5file("cmlh5_Rtest.h5", mode = 'r')


# 2. Check file structure (List groups and datasets) ---
print(file)  #groups and attributes at root level
list.groups(file)  #all groups and subgroups
list.datasets(file)  #all datasets


# 3. Read attributes ---
# 3a. At root level:
att.names <- list.attributes(file)  
att.values <- c()
for (i in 1:length(att.names)){  # loop through all attributes
    att.values[i] <- h5attr(file, att.names[i])
}
print(data.frame(att.names, att.values)) # table with attribute names and values

# 3b. At other levels:
group <- file["cml_1"]
list.attributes(group)
h5attr(group, "cml_id")
h5close(group)

group <- file["cml_1/channel_1"]
list.attributes(group)
h5attr(group, "channel_id")
h5close(group)

dset <- file["cml_1/channel_1/time"]
list.attributes(dset)
h5attr(dset, "unit")
h5close(dset)

# 4. Read data ---
 
# read datasets
dset <- file["cml_1/channel_1/time"]
time <- dset[]
h5close(dset)

dset <- file["cml_1/channel_1/rx"]
rx <- dset[]
h5close(dset)

dset <- file["cml_1/channel_1/tx"]
tx <- dset[]
h5close(dset)

str(data.frame("time" = as.POSIXct(time, origin="1970-01-01"),
               "rx" = rx,
               "tx" =tx))    

# read subsets of data
dset <- file["cml_1/channel_1/time"]
time <- dset[2:11]
h5close(dset)

dset <- file["cml_1/channel_1/rx"]
rx <- dset[2:11]
h5close(dset)

dset <- file["cml_1/channel_1/tx"]
tx <- dset[2:11]
h5close(dset)


str(data.frame("time" = as.POSIXct(time, origin="1970-01-01"),
               "rx" = rx,
               "tx" =tx)) 

# Close file ---
h5close(file)
    

# Manipulate cmlh5 file --------------------------------------------------------

# 1. open cmlh5 file in an append mode ---
file <- h5file("cmlh5_Rtest.h5", mode = 'a')


# 2. add and remove groups or datasets ---
group <- file["cml_2/channel_1"]  # add group
h5close(group)
group <- file["cml_2/channel_2"]  # add group
h5close(group)
file["cml_2/channel_1/rx"] <- 1:10

list.datasets(file)  #list all datasets

# removing a group removes all the subgroups and datasets stored in the group  
h5unlink(file, path="cml_2/channel_1/rx")  # remove dataset rx
h5unlink(file, path="cml_2")  # remove cml_2 group
list.datasets(file)  #list all datasets

# 3. write into dataset (through DataSpace objects) ---
# replace whole dataset: replacement has to have same length as the original
# dataset
dset <- file["cml_1/channel_1/rx"]
d.sp <-  selectDataSpace(dset)  # select whole dataspace
writeDataSet(dset, data = as.numeric(2:21), dspace = d.sp)
h5close(d.sp)
print(dset[])
h5close(dset)

# Replace subset of dataset, this selection type can be slow for many data points 
subs.mtx <- matrix(3:5)  # rows specify datapoints, columns rank
dset <- file["cml_1/channel_1/rx"]
d.sp <-  selectDataSpace(dset, elem = subs.mtx)  
writeDataSet(dset,data = as.numeric(21:23), dspace = d.sp)
h5close(d.sp)
print(dset[])
h5close(dset)

# To speed up selection of larger continuous hyperslab arguments offset and
# count should be used instead subseting method with elem argument.
dset <- file["cml_1/channel_1/rx"]
d.sp <-  selectDataSpace(dset, offset = 3, count = 3)
writeDataSet(dset, data = as.numeric(33:35), dspace = d.sp)
h5close(d.sp)
print(dset[])
h5close(dset)

# 4. Append data to dataset ---
rx.new <- round(rnorm(10, 100, 1)/3, 1)  # new dataset

# extend dataset (to fit the extend of original + new dataset)
dset <- file["cml_1/channel_1/rx"]
d.sp <-  selectDataSpace(dset)  #original DataSpace
dsp.length <- d.sp@count 
extendDataSet(dset, dims = dsp.length + length(rx.new))
h5close(d.sp)
h5close(dset)
# add new data into extended dataset
dset <- file["cml_1/channel_1/rx"]
d.sp <-  selectDataSpace(dset, offset = dsp.length + 1, count = length(rx.new))
writeDataSet(dset, data = rx.new, dspace = d.sp)
h5close(d.sp)
print(dset[])
h5close(dset)

# 5. Close file ---
h5close(file)
