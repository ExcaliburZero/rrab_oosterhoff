rrab:
	csvsql --query "select VName,Type,Per from parameters where Type like 'RRab'" parameters.csv > RRab.csv

curves:
	cat curves_preformated.csv | sed 's/\t/,/g' | tr -d " " > curves.csv
