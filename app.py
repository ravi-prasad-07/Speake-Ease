from flask import Flask, render_template, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

class TreeNode:
    def __init__(self, data=None):
        self.data = data
        self.left = None
        self.right = None

class MorseTree:
    def __init__(self):
        self.root = TreeNode()
        self._build_tree()

    def _build_tree(self):
        morse_codes = [
            ('.-', 'A'), ('-...', 'B'), ('-.-.', 'C'), ('-..', 'D'),
            ('.', 'E'), ('..-.', 'F'), ('--.', 'G'), ('....', 'H'),
            ('..', 'I'), ('.---', 'J'), ('-.-', 'K'), ('.-..', 'L'),
            ('--', 'M'), ('-.', 'N'), ('---', 'O'), ('.--.', 'P'),
            ('--.-', 'Q'), ('.-.', 'R'), ('...', 'S'), ('-', 'T'),
            ('..-', 'U'), ('...-', 'V'), ('.--', 'W'), ('-..-', 'X'),
            ('-.--', 'Y'), ('--..', 'Z'),
            ('.----', '1'), ('..---', '2'), ('...--', '3'), ('....-', '4'),
            ('.....', '5'), ('-....', '6'), ('--...', '7'), ('---..', '8'),
            ('----.', '9'), ('-----', '0')
        ]
        for code, char in morse_codes:
            self.insert(code, char)

    def insert(self, morse_code, char):
        current = self.root
        for symbol in morse_code:
            if symbol == '.':
                if current.left is None:
                    current.left = TreeNode()
                current = current.left
            elif symbol == '-':
                if current.right is None:
                    current.right = TreeNode()
                current = current.right
        current.data = char

    def decode_symbol(self, morse_code):
        current = self.root
        for symbol in morse_code:
            if symbol == '.':
                current = current.left
            elif symbol == '-':
                current = current.right
            if current is None:
                return '?'
        return current.data if current.data else '?'

class Stack:
    def __init__(self):
        self.items = []
    def push(self, item):
        self.items.append(item)
    def pop(self):
        if self.is_empty():
            return None
        return self.items.pop()
    def is_empty(self):
        return len(self.items) == 0
    def get_contents(self):
        return ''.join(self.items)
    def clear(self):
        self.items = []

class Queue:
    def __init__(self):
        self.items = []
    def enqueue(self, item):
        self.items.append(item)
    def dequeue(self):
        if self.is_empty():
            return None
        return self.items.pop(0)
    def is_empty(self):
        return len(self.items) == 0

def validate_input(s):
    for char in s:
        if char not in ['.', '-', '/']:
            return False
    return True

def tokenize_with_stack(morse_input):
    """
    Convert raw Morse string into tokens.
    Special rule: if a symbol sequence is exactly '......',
    we IGNORE it (no token), so .-./...... => only '.-.'
    """
    tokens = []
    symbol_stack = Stack()
    i = 0
    length = len(morse_input)

    while i < length:
        char = morse_input[i]
        if char in '.-':
            symbol_stack.push(char)
        elif char == '/':
            if not symbol_stack.is_empty():
                symbol = symbol_stack.get_contents()
                if symbol != '......':
                    tokens.append(('symbol', symbol))
                symbol_stack.clear()

            if i + 1 < length and morse_input[i + 1] == '/':
                tokens.append(('sep_word', None))
                i += 1
            else:
                tokens.append(('sep_letter', None))
        i += 1

    if not symbol_stack.is_empty():
        symbol = symbol_stack.get_contents()
        if symbol != '......':
            tokens.append(('symbol', symbol))

    return tokens

def decode_morse_with_structures(morse_input, morse_tree):
    tokens = tokenize_with_stack(morse_input)
    token_queue = Queue()
    for token in tokens:
        token_queue.enqueue(token)

    output = ''
    while not token_queue.is_empty():
        token_type, value = token_queue.dequeue()
        if token_type == 'symbol':
            output += morse_tree.decode_symbol(value)
        elif token_type == 'sep_word':
            output += ' '

    return output

morse_tree = MorseTree()

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', decoded='', error='')

@app.route('/decode', methods=['POST'])
def decode():
    morse_input = request.form.get('morse', '').strip()


    if not morse_input:
        return render_template('index.html', decoded='', error='Please enter Morse code.')

    if not validate_input(morse_input):
        return render_template('index.html', decoded='', error='Invalid characters detected. Use only ., -, and /.')

    decoded = decode_morse_with_structures(morse_input, morse_tree)
    return render_template('index.html', decoded=decoded, error='')

if __name__ == '__main__':
    app.run(debug=True, port=5000)