# def convert_to_lines(input_file_path, output_file_path):
#     # Read the content from the input file
#     with open(input_file_path, 'r') as input_file:
#         content = input_file.read()

#     # Split the content by commas and remove leading/trailing whitespaces
#     words = [word.strip() for word in content.split(',')]

#     # Write the words to the output file, each on a new line
#     with open(output_file_path, 'w') as output_file:
#         for word in words:
#             output_file.write(word + '\n')

# # Example usage
# input_path = 'D:\Python Proj\major_vs\ltk.txt'
# output_path = 'D:\Python Proj\major_vs\ine_ltk.txt'

# convert_to_lines(input_path, output_path)











# def clean_and_sort_stopwords(input_file_path, output_file_path):
#     # Read the content from the input file
#     with open(input_file_path, 'r') as input_file:
#         content = input_file.read()

#     # Split the content into lines and remove leading/trailing whitespaces
#     stopwords_list = [word.strip() for word in content.split('\n')]

#     # Remove duplicates and sort alphabetically
#     unique_sorted_stopwords = sorted(set(stopwords_list))

#     # Write the cleaned and sorted stopwords to the output file
#     with open(output_file_path, 'w') as output_file:
#         for word in unique_sorted_stopwords:
#             output_file.write(word + '\n')

# # Example usage
# input_path = 'D:\Python Proj\major_vs\ltk.txt'
# output_path = 'D:\Python Proj\major_vs\cleaned_sorted_stopwords.txt'

# clean_and_sort_stopwords(input_path, output_path)








import os

def create_python_list(input_file_path, output_file_path):
    # Read the content from the input file
    with open(input_file_path, 'r') as input_file:
        content = input_file.read()

    # Split the content into lines and remove leading/trailing whitespaces
    words = [word.strip() for word in content.split('\n')]

    # Get the directory of the output file
    output_directory = os.path.dirname(output_file_path)

    # Create the directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Write the Python list to the output file in one line
    with open(output_file_path, 'w') as output_file:
        output_file.write(f"[{' , '.join([repr(word) for word in words])}]")

# Example usage
input_path = 'D:\Python Proj\major_vs\cleaned_sorted_stopwords.txt'
output_path = 'D:\Python Proj\major_vs\python_list_output.txt'

create_python_list(input_path, output_path) 
