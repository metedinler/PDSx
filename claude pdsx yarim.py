#!/usr/bin/env python3
"""
pdsXv13u - Advanced BASIC Language Interpreter
A comprehensive BASIC programming language interpreter with extended features
Part of the pdsX series by metedinler
Version: 13u

FEATURES:
- Core BASIC language syntax with modern enhancements
- Advanced arithmetic and logical operations
- Comprehensive string manipulation functions
- File I/O operations with multiple formats support
- Graphics capabilities with support for various primitives
- Sound generation and manipulation
- Database connectivity
- Network operations
- Multi-threading support
- External library integration
- Unicode support
- Extended error handling and debugging
- Syntax highlighting and code completion
- Memory management optimizations
- User-defined functions and procedures
- Module imports and namespace management
"""

import sys
import os
import re
import math
import random
import time
import datetime
import json
import csv
import sqlite3
import threading
import queue
import socket
import hashlib
import base64
import argparse
import traceback
import shlex
from typing import Dict, List, Tuple, Union, Optional, Any, Callable

# Optional module imports - will provide warnings if not available
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    print("Warning: NumPy not found. Advanced numeric functions will be limited.")

try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Warning: Matplotlib not found. Advanced plotting will be disabled.")

try:
    import pygame
    HAS_PYGAME = True
    pygame.init()
except ImportError:
    HAS_PYGAME = False
    print("Warning: Pygame not found. Graphics and sound may be limited.")

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("Warning: Requests library not found. Network operations will be limited.")


# Version information
VERSION = "13u"
VERSION_DATE = "2023-11-15"
COPYRIGHT = "Copyright (c) 2023 metedinler"


class TokenType:
    """Token types for the lexer"""
    EOF = "EOF"
    NEWLINE = "NEWLINE"
    NUMBER = "NUMBER"
    IDENT = "IDENT"
    STRING = "STRING"
    
    # Keywords
    LABEL = "LABEL"
    GOTO = "GOTO"
    PRINT = "PRINT"
    INPUT = "INPUT"
    LET = "LET"
    IF = "IF"
    THEN = "THEN"
    ELSE = "ELSE"
    ENDIF = "ENDIF"
    FOR = "FOR"
    TO = "TO"
    STEP = "STEP"
    NEXT = "NEXT"
    WHILE = "WHILE"
    WEND = "WEND"
    DO = "DO"
    UNTIL = "UNTIL"
    LOOP = "LOOP"
    FUNCTION = "FUNCTION"
    RETURN = "RETURN"
    ENDFUNCTION = "ENDFUNCTION"
    SUB = "SUB"
    ENDSUB = "ENDSUB"
    DIM = "DIM"
    DATA = "DATA"
    READ = "READ"
    RESTORE = "RESTORE"
    GOSUB = "GOSUB"
    CALL = "CALL"
    MODULE = "MODULE"
    IMPORT = "IMPORT"
    EXPORT = "EXPORT"
    INCLUDE = "INCLUDE"
    END = "END"
    STOP = "STOP"
    SLEEP = "SLEEP"
    SYSTEM = "SYSTEM"
    REM = "REM"
    
    # Operators
    EQ = "EQ"        # =
    PLUS = "PLUS"    # +
    MINUS = "MINUS"  # -
    MULT = "MULT"    # *
    DIV = "DIV"      # /
    MOD = "MOD"      # %
    POW = "POW"      # ^
    
    # Comparison operators
    EQEQ = "EQEQ"    # ==
    NOTEQ = "NOTEQ"  # <>
    LT = "LT"        # <
    LTEQ = "LTEQ"    # <=
    GT = "GT"        # >
    GTEQ = "GTEQ"    # >=
    
    # Logical operators
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    XOR = "XOR"
    
    # Symbols
    LPAREN = "LPAREN"    # (
    RPAREN = "RPAREN"    # )
    LBRACKET = "LBRACKET"  # [
    RBRACKET = "RBRACKET"  # ]
    COMMA = "COMMA"      # ,
    COLON = "COLON"      # :
    SEMICOLON = "SEMICOLON"  # ;
    DOT = "DOT"          # .
    
    # Special
    COMMENT = "COMMENT"
    ERROR = "ERROR"


class Token:
    """Token class for lexical analysis"""
    def __init__(self, type_: str, value: Any = None, line: int = 0, column: int = 0):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column
        
    def __str__(self) -> str:
        return f"Token({self.type}, {self.value}, {self.line}:{self.column})"
        
    def __repr__(self) -> str:
        return self.__str__()


class Lexer:
    """Lexical analyzer for BASIC code"""
    
    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.current_char = self.source[0] if self.source else None
        self.keywords = {
            "LABEL": TokenType.LABEL,
            "GOTO": TokenType.GOTO,
            "PRINT": TokenType.PRINT,
            "INPUT": TokenType.INPUT,
            "LET": TokenType.LET,
            "IF": TokenType.IF,
            "THEN": TokenType.THEN,
            "ELSE": TokenType.ELSE,
            "ENDIF": TokenType.ENDIF,
            "FOR": TokenType.FOR,
            "TO": TokenType.TO,
            "STEP": TokenType.STEP,
            "NEXT": TokenType.NEXT,
            "WHILE": TokenType.WHILE,
            "WEND": TokenType.WEND,
            "DO": TokenType.DO,
            "UNTIL": TokenType.UNTIL,
            "LOOP": TokenType.LOOP,
            "FUNCTION": TokenType.FUNCTION,
            "RETURN": TokenType.RETURN,
            "ENDFUNCTION": TokenType.ENDFUNCTION,
            "SUB": TokenType.SUB,
            "ENDSUB": TokenType.ENDSUB,
            "DIM": TokenType.DIM,
            "DATA": TokenType.DATA,
            "READ": TokenType.READ,
            "RESTORE": TokenType.RESTORE,
            "GOSUB": TokenType.GOSUB,
            "CALL": TokenType.CALL,
            "MODULE": TokenType.MODULE,
            "IMPORT": TokenType.IMPORT,
            "EXPORT": TokenType.EXPORT,
            "INCLUDE": TokenType.INCLUDE,
            "END": TokenType.END,
            "STOP": TokenType.STOP,
            "SLEEP": TokenType.SLEEP,
            "SYSTEM": TokenType.SYSTEM,
            "REM": TokenType.REM,
            "AND": TokenType.AND,
            "OR": TokenType.OR,
            "NOT": TokenType.NOT,
            "XOR": TokenType.XOR,
            "MOD": TokenType.MOD
        }
    
    def advance(self):
        """Move to the next character in the source code"""
        self.position += 1
        if self.position >= len(self.source):
            self.current_char = None
        else:
            self.current_char = self.source[self.position]
            self.column += 1
    
    def peek(self, offset: int = 1) -> Optional[str]:
        """Look ahead characters without advancing position"""
        peek_pos = self.position + offset
        if peek_pos >= len(self.source):
            return None
        return self.source[peek_pos]
    
    def skip_whitespace(self):
        """Skip whitespace characters except newlines"""
        while self.current_char and self.current_char.isspace() and self.current_char != '\n':
            self.advance()
    
    def skip_comment(self):
        """Skip comments (REM or ')"""
        while self.current_char and self.current_char != '\n':
            self.advance()
    
    def process_number(self) -> Token:
        """Process a numeric token (integer or float)"""
        start_col = self.column
        result = ""
        is_float = False
        
        # Handle digits before decimal point
        while self.current_char and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                if is_float:  # Second decimal point is not allowed
                    return Token(TokenType.ERROR, "Invalid number format: multiple decimal points", self.line, start_col)
                is_float = True
            result += self.current_char
            self.advance()
        
        # Handle scientific notation
        if self.current_char and self.current_char.lower() == 'e':
            result += self.current_char
            self.advance()
            
            # Handle optional +/- after 'e'
            if self.current_char in ['+', '-']:
                result += self.current_char
                self.advance()
            
            # Must have at least one digit after 'e'
            if not self.current_char or not self.current_char.isdigit():
                return Token(TokenType.ERROR, "Invalid scientific notation format", self.line, start_col)
            
            # Handle digits in exponent
            while self.current_char and self.current_char.isdigit():
                result += self.current_char
                self.advance()
            
            is_float = True
        
        # Convert to appropriate numeric type
        try:
            if is_float:
                value = float(result)
            else:
                value = int(result)
            return Token(TokenType.NUMBER, value, self.line, start_col)
        except ValueError:
            return Token(TokenType.ERROR, f"Invalid number format: {result}", self.line, start_col)
    
    def process_identifier(self) -> Token:
        """Process an identifier or keyword"""
        start_col = self.column
        result = ""
        
        # First character must be a letter
        if self.current_char and self.current_char.isalpha():
            result += self.current_char
            self.advance()
        else:
            return Token(TokenType.ERROR, "Identifier must start with a letter", self.line, start_col)
        
        # Subsequent characters can be alphanumeric or underscore
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        
        # Check if it's a keyword (convert to uppercase for case-insensitivity)
        upper_result = result.upper()
        if upper_result in self.keywords:
            return Token(self.keywords[upper_result], upper_result, self.line, start_col)
        
        # Handle special type markers ($, %, &, !)
        if self.current_char in ['$', '%', '&', '!']:
            result += self.current_char
            self.advance()
        
        # It's a regular identifier
        return Token(TokenType.IDENT, result, self.line, start_col)
    
    def process_string(self) -> Token:
        """Process a string literal"""
        start_col = self.column
        self.advance()  # Skip the opening quote
        result = ""
        
        while self.current_char and self.current_char != '"':
            # Handle escape sequences
            if self.current_char == '\\' and self.peek():
                self.advance()
                if self.current_char == 'n':
                    result += '\n'
                elif self.current_char == 't':
                    result += '\t'
                elif self.current_char == 'r':
                    result += '\r'
                elif self.current_char == '"':
                    result += '"'
                elif self.current_char == '\\':
                    result += '\\'
                else:
                    result += '\\' + self.current_char
            else:
                result += self.current_char
            
            self.advance()
            
            if not self.current_char:
                return Token(TokenType.ERROR, "Unterminated string literal", self.line, start_col)
        
        self.advance()  # Skip the closing quote
        return Token(TokenType.STRING, result, self.line, start_col)
    
    def get_next_token(self) -> Token:
        """Get the next token from the source code"""
        while self.current_char:
            # Skip whitespace
            if self.current_char.isspace() and self.current_char != '\n':
                self.skip_whitespace()
                continue
            
            # Handle newlines
            if self.current_char == '\n':
                token = Token(TokenType.NEWLINE, None, self.line, self.column)
                self.advance()
                self.line += 1
                self.column = 1
                return token
            
            # Handle numbers
            if self.current_char.isdigit():
                return self.process_number()
            
            # Handle identifiers and keywords
            if self.current_char.isalpha():
                return self.process_identifier()
            
            # Handle strings
            if self.current_char == '"':
                return self.process_string()
            
            # Handle comments
            if self.current_char == "'" or (self.current_char == 'R' and self.peek() == 'E' and self.peek(2) == 'M'):
                token = Token(TokenType.COMMENT, None, self.line, self.column)
                self.skip_comment()
                return token
            
            # Handle operators and symbols
            if self.current_char == '=':
                start_col = self.column
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.EQEQ, "==", self.line, start_col)
                return Token(TokenType.EQ, "=", self.line, start_col)
            
            if self.current_char == '+':
                start_col = self.column
                self.advance()
                return Token(TokenType.PLUS, "+", self.line, start_col)
            
            if self.current_char == '-':
                start_col = self.column
                self.advance()
                return Token(TokenType.MINUS, "-", self.line, start_col)
            
            if self.current_char == '*':
                start_col = self.column
                self.advance()
                return Token(TokenType.MULT, "*", self.line, start_col)
            
            if self.current_char == '/':
                start_col = self.column
                self.advance()
                return Token(TokenType.DIV, "/", self.line, start_col)
            
            if self.current_char == '%':
                start_col = self.column
                self.advance()
                return Token(TokenType.MOD, "%", self.line, start_col)
            
            if self.current_char == '^':
                start_col = self.column
                self.advance()
                return Token(TokenType.POW, "^", self.line, start_col)
            
            if self.current_char == '<':
                start_col = self.column
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.LTEQ, "<=", self.line, start_col)
                elif self.current_char == '>':
                    self.advance()
                    return Token(TokenType.NOTEQ, "<>", self.line, start_col)
                return Token(TokenType.LT, "<", self.line, start_col)
            
            if self.current_char == '>':
                start_col = self.column
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.GTEQ, ">=", self.line, start_col)
                return Token(TokenType.GT, ">", self.line, start_col)
            
            if self.current_char == '(':
                start_col = self.column
                self.advance()
                return Token(TokenType.LPAREN, "(", self.line, start_col)
            
            if self.current_char == ')':
                start_col = self.column
                self.advance()
                return Token(TokenType.RPAREN, ")", self.line, start_col)
            
            if self.current_char == '[':
                start_col = self.column
                self.advance()
                return Token(TokenType.LBRACKET, "[", self.line, start_col)
            
            if self.current_char == ']':
                start_col = self.column
                self.advance()
                return Token(TokenType.RBRACKET, "]", self.line, start_col)
            
            if self.current_char == ',':
                start_col = self.column
                self.advance()
                return Token(TokenType.COMMA, ",", self.line, start_col)
            
            if self.current_char == ':':
                start_col = self.column
                self.advance()
                return Token(TokenType.COLON, ":", self.line, start_col)
            
            if self.current_char == ';':
                start_col = self.column
                self.advance()
                return Token(TokenType.SEMICOLON, ";", self.line, start_col)
            
            if self.current_char == '.':
                start_col = self.column
                self.advance()
                return Token(TokenType.DOT, ".", self.line, start_col)
            
            # Handle unknown characters
            error_msg = f"Unknown character: {self.current_char}"
            token = Token(TokenType.ERROR, error_msg, self.line, self.column)
            self.advance()
            return token
        
        # End of file
        return Token(TokenType.EOF, None, self.line, self.column)
    
    def tokenize(self) -> List[Token]:
        """Tokenize the entire source code"""
        tokens = []
        token = self.get_next_token()
        
        while token.type != TokenType.EOF:
            tokens.append(token)
            token = self.get_next_token()
        
        tokens.append(token)  # Add EOF token
        return tokens


# Node classes for AST (Abstract Syntax Tree)
class ASTNode:
    """Base class for all AST nodes"""
    pass


class ProgramNode(ASTNode):
    """Root node of the AST"""
    def __init__(self, statements):
        self.statements = statements


class StatementNode(ASTNode):
    """Base class for statement nodes"""
    pass


class PrintNode(StatementNode):
    """PRINT statement node"""
    def __init__(self, expressions, newline=True):
        self.expressions = expressions
        self.newline = newline


class LetNode(StatementNode):
    """LET (assignment) statement node"""
    def __init__(self, variable, expression):
        self.variable = variable
        self.expression = expression


class InputNode(StatementNode):
    """INPUT statement node"""
    def __init__(self, prompt, variables):
        self.prompt = prompt
        self.variables = variables


class IfNode(StatementNode):
    """IF statement node"""
    def __init__(self, condition, then_statements, else_statements=None):
        self.condition = condition
        self.then_statements = then_statements
        self.else_statements = else_statements


class ForNode(StatementNode):
    """FOR loop node"""
    def __init__(self, variable, start_expr, end_expr, step_expr, statements):
        self.variable = variable
        self.start_expr = start_expr
        self.end_expr = end_expr
        self.step_expr = step_expr
        self.statements = statements


class WhileNode(StatementNode):
    """WHILE loop node"""
    def __init__(self, condition, statements):
        self.condition = condition
        self.statements = statements


class DoUntilNode(StatementNode):
    """DO-UNTIL loop node"""
    def __init__(self, statements, condition, check_at_start=True):
        self.statements = statements
        self.condition = condition
        self.check_at_start = check_at_start


class FunctionNode(StatementNode):
    """Function definition node"""
    def __init__(self, name, parameters, statements, return_expr=None):
        self.name = name
        self.parameters = parameters
        self.statements = statements
        self.return_expr = return_expr


class SubNode(StatementNode):
    """Subroutine definition node"""
    def __init__(self, name, parameters, statements):
        self.name = name
        self.parameters = parameters
        self.statements = statements


class ReturnNode(StatementNode):
    """RETURN statement node"""
    def __init__(self, expression=None):
        self.expression = expression


class CallNode(StatementNode):
    """Function/subroutine call node"""
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments


class DimNode(StatementNode):
    """DIM (array declaration) node"""
    def __init__(self, variable, dimensions):
        self.variable = variable
        self.dimensions = dimensions


class DataNode(StatementNode):
    """DATA statement node"""
    def __init__(self, values):
        self.values = values


class ReadNode(StatementNode):
    """READ statement node"""
    def __init__(self, variables):
        self.variables = variables


class RestoreNode(StatementNode):
    """RESTORE statement node"""
    def __init__(self, label=None):
        self.label = label


class LabelNode(StatementNode):
    """LABEL statement node"""
    def __init__(self, name):
        self.name = name


class GotoNode(StatementNode):
    """GOTO statement node"""
    def __init__(self, label):
        self.label = label


class GosubNode(StatementNode):
    """GOSUB statement node"""
    def __init__(self, label):
        self.label = label


class ModuleNode(StatementNode):
    """MODULE definition node"""
    def __init__(self, name, statements):
        self.name = name
        self.statements = statements


class ImportNode(StatementNode):
    """IMPORT statement node"""
    def __init__(self, module_name, symbols=None):
        self.module_name = module_name
        self.symbols = symbols  # What to import from the module (None for all)


class ExportNode(StatementNode):
    """EXPORT statement node"""
    def __init__(self, symbols):
        self.symbols = symbols


class IncludeNode(StatementNode):
    """INCLUDE statement node"""
    def __init__(self, filename):
        self.filename = filename


class EndNode(StatementNode):
    """END statement node"""
    pass


class StopNode(StatementNode):
    """STOP statement node"""
    pass


class SleepNode(StatementNode):
    """SLEEP statement node"""
    def __init__(self, duration):
        self.duration = duration


class SystemNode(StatementNode):
    """SYSTEM (shell command) node"""
    def __init__(self, command):
        self.command = command


# Expression nodes
class ExpressionNode(ASTNode):
    """Base class for expression nodes"""
    pass


class BinaryOpNode(ExpressionNode):
    """Binary operation node"""
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right


class UnaryOpNode(ExpressionNode):
    """Unary operation node"""
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr


class NumberNode(ExpressionNode):
    """Number literal node"""
    def __init__(self, value):
        self.value = value


class StringNode(ExpressionNode):
    """String literal node"""
    def __init__(self, value):
        self.value = value


class VariableNode(ExpressionNode):
    """Variable reference node"""
    def __init__(self, name):
        self.name = name


class ArrayAccessNode(ExpressionNode):
    """Array access node"""
    def __init__(self, name, indices):
        self.name = name
        self.indices = indices


class FunctionCallNode(ExpressionNode):
    """Function call in expression context"""
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments


class Parser:
    """Parser for BASIC language to create an AST from tokens"""
    
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0
        self.current_token = self.tokens[0] if self.tokens else None
        
    def advance(self):
        """Move to the next token"""
        self.position += 1
        if self.position < len(self.tokens):
            self.current_token = self.tokens[self.position]
        else:
            self.current_token = None
    
    def peek(self, offset=1):
        """Look ahead tokens without advancing"""
        peek_pos = self.position + offset
        if peek_pos < len(self.tokens):
            return self.tokens[peek_pos]
        return None
    
    def expect(self, type_):
        """Check if current token is of expected type and advance"""
        if self.current_token and self.current_token.type == type_:
            token = self.current_token
            self.advance()
            return token
        raise SyntaxError(f"Expected {type_}, got {self.current_token.type if self.current_token else 'EOF'}")
    
    def parse(self):
        """Parse the program"""
        statements = self.parse_statements()
        return ProgramNode(statements)
    
    def parse_statements(self):
        """Parse a list of statements"""
        statements = []
        
        while self.current_token and self.current_token.type != TokenType.EOF:
            # Skip newlines and comments
            while self.current_token and (self.current_token.type == TokenType.NEWLINE or 
                                           self.current_token.type == TokenType.COMMENT):
                self.advance()
                
            if not self.current_token or self.current_token.type == TokenType.EOF:
                break
                
            statement = self.parse_statement()
            if statement:
                statements.append(statement)
                
            # Skip newlines and comments after statement
            while self.current_token and (self.current_token.type == TokenType.NEWLINE or 
                                           self.current_token.type == TokenType.COMMENT):
                self.advance()
        
        return statements
    
    def parse_statement(self):
        """Parse a single statement"""
        if not self.current_token:
            return None
            
        if self.current_token.type == TokenType.PRINT:
            return self.parse_print_statement()
        elif self.current_token.type == TokenType.LET:
            return self.parse_let_statement()
        elif self.current_token.type == TokenType.INPUT:
            return self.parse_input_statement()
        elif self.current_token.type == TokenType.IF:
            return self.parse_if_statement()
        elif self.current_token.type == TokenType.FOR:
            return self.parse_for_statement()
        elif self.current_token.type == TokenType.WHILE:
            return self.parse_while_statement()
        elif self.current_token.type == TokenType.DO:
            return self.parse_do_statement()
        elif self.current_token.type == TokenType.FUNCTION:
            return self.parse_function_statement()
        elif self.current_token.type == TokenType.SUB:
            return self.parse_sub_statement()
        elif self.current_token.type == TokenType.RETURN:
            return self.parse_return_statement()
        elif self.current_token.type == TokenType.CALL:
            return self.parse_call_statement()
        elif self.current_token.type == TokenType.DIM:
            return self.parse_dim_statement()
        elif self.current_token.type == TokenType.DATA:
            return self.parse_data_statement()
        elif self.current_token.type == TokenType.READ:
            return self.parse_read_statement()
        elif self.current_token.type == TokenType.RESTORE:
            return self.parse_restore_statement()
        elif self.current_token.type == TokenType.LABEL:
            return self.parse_label_statement()
        elif self.current_token.type == TokenType.GOTO:
            return self.parse_goto_statement()
        elif self.current_token.type == TokenType.GOSUB:
            return self.parse_gosub_statement()
        elif self.current_token.type == TokenType.MODULE:
            return self.parse_module_statement()
        elif self.current_token.type == TokenType.IMPORT:
            return self.parse_import_statement()
        elif self.current_token.type == TokenType.EXPORT:
            return self.parse_export_statement()
        elif self.current_token.type == TokenType.INCLUDE:
            return self.parse_include_statement()
        elif self.current_token.type == TokenType.END:
            return self.parse_end_statement()
        elif self.current_token.type == TokenType.STOP:
            return self.parse_stop_statement()
        elif self.current_token.type == TokenType.SLEEP:
            return self.parse_sleep_statement()
        elif self.current_token.type == TokenType.SYSTEM:
            return self.parse_system_statement()
        elif self.current_token.type == TokenType.IDENT:
            # Could be an implicit LET statement or function call
            if self.peek() and (self.peek().type == TokenType.EQ or 
                               self.peek().type == TokenType.LBRACKET):
                return self.parse_let_statement(implicit=True)
            else:
                return self.parse_call_statement(implicit=True)
        else:
            raise SyntaxError(f"Unexpected token: {self.current_token}")
    
    def parse_print_statement(self):
        """Parse PRINT statement"""
        self.expect(TokenType.PRINT)
        expressions = []
        newline = True
        
        if self.current_token an