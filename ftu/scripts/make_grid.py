from ftu.FreThaw1D_gridcreator import main as make_grid


def main():
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    
    parser.add_argument('-d', '--dz-min', dest="dz_min", default=0.005, type=float)
    parser.add_argument('-b', dest='b', default=0.1, type=float)
    parser.add_argument('-i', '--interp-model', dest='interp_model', default='linear', type=str)
    parser.add_argument('-g', '--grid-type', choices=["exponential", "classical"], default='exponential', dest="grid_type")
    parser.add_argument('-s', '--output-summary', dest='output_summary',type=str, default='')
    parser.add_argument('-t', '--output-title', dest='output_title',type=str, default='')
    parser.add_argument('-n', '--output-institution', dest='output_institution',type=str, default='')
    parser.add_argument('-C', '--Initial-Condition', dest="ic_input_file_name" )
    parser.add_argument('-G', '--Grid-Input', dest="grid_input_file_name")
    parser.add_argument('-P', '--Parameter-Input', dest="parameter_input_file_name")
    parser.add_argument("-O", '--Output', type=str, dest="output_file_name")

    args = parser.parse_args()
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
    
    make_grid(args)


if __name__ == "__main__":
    main()
