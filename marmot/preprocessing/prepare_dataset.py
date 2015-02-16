import argparse
import sys, codecs, pickle
import numpy as np
import pandas as pd

import preprocess_wmt
import preprocess_ter

# prepare a dataset for the Machine Learning component
# sample call: python prepare_dataset.py -i test_data/training -v /home/chris/programs/word2vec/trunk/vectors.bin -o 'test-'

def array_to_df(array):
    df = pd.DataFrame(array, index=range(array.shape[0]), columns=range(array.shape[1]))
    return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i','--input', type=str, required=True, help='input file -- sentences tagged with errors')
    parser.add_argument('-v','--vector', type=str, required=True, help='vectors generated by word2vec in binary format')
    parser.add_argument('-t', '--test', type=str, help='test data (file in the same format as input)')
    parser.add_argument('-o', '--output', type=str, default='', help='output file prefix')
    parser.add_argument('-p', '--preprocessor', type=str, default='xml', choices=['ter', 'xml'], help='output file: labels for test data')

    args = parser.parse_args()
    text_processor = None
    if args.preprocessor == 'xml':
        text_processor = preprocess_wmt.parse_src
    elif args.preprocessor == 'ter':
        text_processor = preprocess_ter.parse_ter_file
    else:
        text_processor = preprocess_wmt.parse_src

    # TODO: all of the following code could be parallelized
    train_features = text_processor(args.input, good_context=True)
    train_tokens = [x[2] for x in train_features]
    sentence_ids = [x[0] for x in train_features]

    (train_vecs, train_labels) = get_features.get_features(args.vector, feature_array=train_features)
    # Create dataframes
    train_df = array_to_df(train_vecs)
    train_df['sentence_id'] = pd.Series(sentence_ids, index=train_df.index)
    train_df['token'] = pd.Series(train_tokens, index=train_df.index)
    # add labels column to dataframe
    train_df['label'] = pd.Series(train_labels, index=train_df.index)
    # save dataframes as csv
    train_df.to_csv(args.output + 'train.csv', encoding='utf-8')

    # pickle train_features for later
    with open('train_features.pickle', 'w') as out:
        pickle.dump(train_features, out)

    if args.test:
        test_features = text_processor( args.test, good_context=True)
        (test_vecs, test_labels) = get_features.get_features(args.vector, feature_array=test_features)
        test_tokens = [x[2] for x in test_features]
        test_df = array_to_df(test_vecs)
        test_df['token'] = pd.Series(test_tokens, index=test_df.index)
        test_df['label'] = pd.Series(test_labels, index=test_df.index)
        test_df.to_csv(args.output + 'test.csv', encoding='utf-8')

    sys.stderr.write("Finished preprocessing test/train data, and extracting vectors")
