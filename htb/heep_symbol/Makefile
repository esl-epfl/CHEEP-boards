heepocrates.csv: heepocrates_kipart_csv.py clean
	python heepocrates_kipart_csv.py

heepocrates.lib: heepocrates.csv
	kipart --overwrite heepocrates.csv

clean:
	rm -rf heepocrates.csv
	rm -rf heepocrates.lib