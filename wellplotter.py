"""
    Author: Alejandro Sifrim
    Affiliation: Wellcome Trust Sanger Institute/KU Leuven
    
    Description

    Aggregates a set of plots according to their respective place in a 96-well plate

    Parameters
    ----------

    1) A file mapping the identifiers to their position on the plate using barcodes
    2) Directory containing the images to be aggregated must be present which start with the aggregated barcode
     (e.g. "TGCAGCTA-AAGGAGTA.160812_Maria_Xydia_GandT.160902.HiSeq2500.FCA.lane5.gcap_16_04.R1.fastq.gz.gene.avgprof.pdf")
    

    - i7 ids denote column identifiers (12 columns)
    - i5 ids denote row identifiers (8 rows)
    
    Returns
    -------
    
"""
import sys
import os
import csv
import time
import pprint
import glob

from PIL import Image


today = time.strftime('%Y%m%d') 
pp = pprint.PrettyPrinter(indent=4)

def read_set(set_file):
	res = {}
	for row in csv.DictReader(open(set_file,'r'),delimiter="\t"):
		res[row["concat"]] = {
			"sample_number": row["sample_number"],
			"i5": row["i5"],
			"i7": row["i7"],
			"plot": ""
			}
		sample_number_to_coordinates(row["sample_number"])
	return res

def create_plot_hash(directory):
	files = glob.glob(directory+"/*.png")
	plothash = {}
	for f in files:
		basename =  os.path.basename(f)
		barcode = basename.split('.')[0]
		plothash[barcode] = f
	return plothash

def find_plots(sample_hash, plot_hash):
	for (barcode, sample) in sample_hash.iteritems():
		if barcode in plot_hash:
			sample_hash[barcode]["plot"] = plot_hash[barcode]
		else:
			sample_hash[barcode]["plot"] = "NA"
	return sample_hash

def sample_number_to_coordinates(sample_number):
	sample_number = int(sample_number)-1
	row_id = sample_number/12
	col_id = sample_number%12
	x = 50 + col_id*100
	y = 50 + row_id*100
	return (x,y)

def aggregate_plots(sample_hash,output_path):
	new_image = Image.new("RGB",(1300,900),"white")
	for (barcode,sample) in sample_hash.iteritems():
		if sample["plot"] == "NA":
			continue
		image = Image.open(sample["plot"])
		image =	Image.composite(image, Image.new('RGB', image.size, 'white'), image)
		box = (50,70,1200,960)
		region = image.crop(box)
		region = region.resize((100,100),Image.ANTIALIAS)
		coords = sample_number_to_coordinates(sample["sample_number"])
		new_image.paste(region,coords)

	new_image.save(output_path,'PNG')

def main():
    sample_hash = read_set(sys.argv[1])
    plot_hash = create_plot_hash(sys.argv[2])
    sample_hash = find_plots(sample_hash, plot_hash)
    output_path = sys.argv[1]+".aggregate_plot.png"
    aggregate_plots(sample_hash,output_path)

if __name__ == "__main__":
    main()
        