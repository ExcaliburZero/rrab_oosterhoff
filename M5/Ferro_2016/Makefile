rrab:
	csvsql --query "select VName,VType,Per from asu where VType like '%RRab%'" asu.csv > RRab.csv

curves:
	cat curves_preformat.csv | sed 's/\t/,/g' | tr -d " " > curves.csv
