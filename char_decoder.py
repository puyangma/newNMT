#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CS224N 2018-19: Homework 5
"""

import torch
import torch.nn as nn

class CharDecoder(nn.Module):
    def __init__(self, hidden_size, char_embedding_size=50, target_vocab=None):
        """ Init Character Decoder.

        @param hidden_size (int): Hidden size of the decoder LSTM
        @param char_embedding_size (int): dimensionality of character embeddings
        @param target_vocab (VocabEntry): vocabulary for the target language. See vocab.py for documentation.
        """
        ### YOUR CODE HERE for part 2a
        super(CharDecoder, self).__init__()
        self.pad_idx = target_vocab.char2id['<pad>']
        self.embed_size = char_embedding_size
        self.hidden_size = hidden_size
        self.target_vocab = target_vocab
        self.charDecoder = nn.LSTM(input_size=self.embed_size, hidden_size=hidden_size, bias=True, bidirectional=False)
        self.char_output_projection = nn.Linear(self.hidden_size, len(self.target_vocab.char2id), bias=True)
        self.loss = nn.CrossEntropyLoss(ignore_index=self.target_vocab.char2id['<pad>'], reduction='sum')
        self.decoderCharEmb = nn.Embedding(len(target_vocab.char2id), embedding_dim=self.embed_size, padding_idx=self.pad_idx)
        self.softmax = nn.Softmax(dim=-1)

        ### TODO - Initialize as an nn.Module.
        ###      - Initialize the following variables:
        ###        self.charDecoder: LSTM. Please use nn.LSTM() to construct this.
        ###        self.char_output_projection: Linear layer, called W_{dec} and b_{dec} in the PDF
        ###        self.decoderCharEmb: Embedding matrix of character embeddings
        ###        self.target_vocab: vocabulary for the target language
        ###
        ### Hint: - Use target_vocab.char2id to access the character vocabulary for the target language.
        ###       - Set the padding_idx argument of the embedding matrix.
        ###       - Create a new Embedding layer. Do not reuse embeddings created in Part 1 of this assignment.
        

        ### END YOUR CODE


    
    def forward(self, input, dec_hidden=None):
        """ Forward pass of character decoder.

        @param input: tensor of integers, shape (length, batch)
        @param dec_hidden: internal state of the LSTM before reading the input characters. A tuple of two tensors of shape (1, batch, hidden_size)

        @returns scores: called s_t in the PDF, shape (length, batch, self.vocab_size)
        @returns dec_hidden: internal state of the LSTM after reading the input characters. A tuple of two tensors of shape (1, batch, hidden_size)
        """
        ### YOUR CODE HERE for part 2b
        ### TODO - Implement the forward pass of the character decoder.
        X = self.decoderCharEmb(input)
        val, (hidden, cell) = self.charDecoder(X, dec_hidden)
        scores = self.char_output_projection(val)
        return scores, (hidden, cell)
        
        
        ### END YOUR CODE 


    def train_forward(self, char_sequence, dec_hidden=None):
        """ Forward computation during training.

        @param char_sequence: tensor of integers, shape (length, batch). Note that "length" here and in forward() need not be the same.
        @param dec_hidden: initial internal state of the LSTM, obtained from the output of the word-level decoder. A tuple of two tensors of shape (1, batch, hidden_size)

        @returns The cross-entropy loss, computed as the *sum* of cross-entropy losses of all the words in the batch.
        """
        ### YOUR CODE HERE for part 2c
        ### TODO - Implement training forward pass.
        char_sequence = char_sequence.contiguous()
        scores, (hidden, cell) = self.forward(char_sequence[:-1], dec_hidden)
        scores = scores.permute(0, 2, 1)
        loss = self.loss(scores, char_sequence[1:])
        return loss
        ###
        ### Hint: - Make sure padding characters do not contribute to the cross-entropy loss.
        ###       - char_sequence corresponds to the sequence x_1 ... x_{n+1} from the handout (e.g., <START>,m,u,s,i,c,<END>).


        ### END YOUR CODE

    def decode_greedy(self, initialStates, device, max_length=21):
        """ Greedy decoding
        @param initialStates: initial internal state of the LSTM, a tuple of two tensors of size (1, batch, hidden_size)
        @param device: torch.device (indicates whether the model is on CPU or GPU)
        @param max_length: maximum length of words to decode

        @returns decodedWords: a list (of length batch) of strings, each of which has length <= max_length.
                              The decoded strings should NOT contain the start-of-word and end-of-word characters.
        """

        ### YOUR CODE HERE for part 2d
        decodedWords = []
        chars=[]
        batch_size = initialStates[0].shape[1]
        charsnow = torch.tensor([self.target_vocab.start_of_word]*batch_size, device=device).unsqueeze(0)
        for i in range(max_length):
            scores, (hidden, cell) = self.forward(charsnow, initialStates)
            initialStates = (hidden, cell)
            pt = self.softmax(scores)
            charsnow = torch.argmax(pt.squeeze(0), dim=-1).unsqueeze(0)
            chars.append(charsnow.squeeze(0))

        index = torch.stack(chars).permute(1,0)
        char_index = torch.split(index, 1, dim=0)

        for idx in char_index:
            w =''
            for i in idx.squeeze(0):
                i = int(i)
                if i == self.target_vocab.end_of_word:
                    break
                w = w + str(self.target_vocab.id2char[i])
            if len(w) > max_length:
                w = w[:max_length]
            decodedWords.append(w)
        return decodedWords


        ### TODO - Implement greedy decoding.
        ### Hints:
        ###      - Use target_vocab.char2id and target_vocab.id2char to convert between integers and characters
        ###      - Use torch.tensor(..., device=device) to turn a list of character indices into a tensor.
        ###      - We use curly brackets as start-of-word and end-of-word characters. That is, use the character '{' for <START> and '}' for <END>.
        ###        Their indices are self.target_vocab.start_of_word and self.target_vocab.end_of_word, respectively.
        
        
        ### END YOUR CODE

