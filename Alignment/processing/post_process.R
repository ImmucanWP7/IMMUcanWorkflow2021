#!/usr/bin/env Rscript
args <- commandArgs(trailingOnly=TRUE)

# Check length of inputs
if (length(args) != 1) {
    stop("Please specify a single path.")
}

# Check if dir exists
cur_dir <- args[1]
if (!dir.exists(cur_dir)) {
    stop(cur_dir, " does not exist")
}

# Check if .csv files exists
cur_files <- list.files(cur_dir, pattern = "*.csv", full.names = TRUE)
if (length(cur_files) == 0) {
    stop("No .csv files specified")
}

# We will now need to add the W, H and Name column
# We also need to subtract 300 from the X value and add 300 to the Y value to find the starting value of the ROI
for (i in cur_files) {
    cur_file <- suppressWarnings(read.csv(i, header = TRUE, stringsAsFactors = FALSE))
    
    # Check if file was already altered
    if (all(c("W", "H", "Name") %in% colnames(cur_file))) {
        next
    } else {
        # Change coordinates
        cur_file$X <- cur_file$X - 300
        cur_file$Y <- cur_file$Y + 300
        
        # Add width and height
        cur_file$W <- 600
        cur_file$H <- 600
        
        # Add position
        if (substr(basename(i), 1, 1) == "S") {
            cur_pos <- strsplit(x = basename(i), split = "_")[[1]][2]
            cur_file$Name <- paste0("pos", cur_pos, "_", seq_len(nrow(cur_file)))
        } else {
            cur_file$Name <- paste0("pos1_", seq_len(nrow(cur_file)))
        }
        
        # Write out files
        write.csv(cur_file,
                  file = paste0(sub("\\.csv", "", i), "_mod.csv"),
                  quote = FALSE, row.names = FALSE)
   }
}



