import pathlib as Path
import pegpy
#from pegpy.tpeg import ParseTree
peg = pegpy.grammar('cj.tpeg')
parser = pegpy.generate(peg)

tree = parser('跳ね返り係数は0.5')
# print(repr(tree))
print('@debug(input) ', list(tree))

property = {'色': 'fillStyle', 
            # '形': 'shape',
            # '位置': 'position',
            # '幅': 'width',
            # '高さ': 'height',
            # '透明度': 'opacity',
            # '傾き': 'angle',
            # '質量': 'mass',
            # '密度': 'density',
            # '速度': 'velocity',
            '摩擦': 'friction',
            # '空気摩擦': 'frictionAir',         # モデル登録なし
            # '静止摩擦力': 'frictionStatic',    # モデル登録なし
            '固定': 'isStatic',
            # 'センサー': 'isSensor',
            '跳ねる': 'restitution',
            '反発係数': 'restitution'}

fillStyle = {'赤': '#e60033',
             'ピンク': '#f5b2b2'}

angle = {}

friction = {'pos': '0.001',
            'neg': '0.0000001'}

isStatic = {'pos': 'True',
            'neg': 'False'}

restitution = {'more': '1.2',
               'pos': '1.0',
               'little': '0.7',
               'neg': '0.0'}


model_dir = 'nlp_dict/entity_vector.model.bin'

class Expr(object):
  pass

class Let(Expr):
  left: Expr
  right: Expr
  key: str
  value: str

  def __init__(self, left, right):
    self.left = left
    self.right = right

  def translate(self):
    # left, right から  key, value に変換する
    if self.left in property:
      key = property[self.left]
    else:
      from gensim.models import KeyedVectors
      model = KeyedVectors.load_word2vec_format(model_dir, binary=True)
      if self.left not in model:
        return None
      sim_max = 0.0
      sim_word = None
      for word in list(property.keys()):
        sim = model.similarity(word, self.left)
        if sim > sim_max:
          sim_max = sim
          sim_word = word
      key = property[sim_word]
    
    if self.right == '赤':
      value = '赤'
    
    return key, value

  # def emit(self):
  #   self.translate(self)
  #   return f'{self.key} = {self.value}'
  #   return f'{key} = {self.right}'


class Verb(Expr):
  key: str
  value: str
  def __init__(self, domain: str, neg: bool):
    self.domain = domain
    self.neg = neg

  def translate(self):
    # left, right から  key, value に変換する
    if self.domain in property:
      key = property[self.domain]
    else:
      from gensim.models import KeyedVectors
      model = KeyedVectors.load_word2vec_format(model_dir, binary=True)
      if self.domain not in model:
        return None
      sim_max = 0.0
      sim_word = None
      for word in list(property.keys()):
        sim = model.similarity(word, self.domain)
        if sim > sim_max:
          sim_max = sim
          sim_word = word
      key = property[sim_word]

    if key == 'restitution':
      if self.neg == True:
        value = restitution['neg']
      else:
        value = restitution['pos']

    return key, value

  # def emit(self):
  #   return f'{self.value}'

# e = Verb('書く')
# isinstance(e, Verb) # 種類
# translate


def conv(tree) :
  if tree == 'S':
    print('@debug(str) ', str(tree))
    if tree[0] == 'NounChunk' and tree[1] == 'NounChunk':
      left = tree[0]
      right = tree[1]
      return Let(conv(left[0]), str(right))

    if tree[0] == 'Adverb' and tree[1] == 'VerbChunk':
      # e.g.: [#Adverb 'よく'][#VerbChunk[#Verb1 '跳ね'][#Do 'る']]
      # e.g.: [#Adverb '全く'][#VerbChunk[#Verb1 '跳ね'][#DoNot 'ない']]
      # e.g.: [#Adverb 'あまり'][#VerbChunk[#Verb1 '跳ね'][#DoNot 'ない']]

      return 0

    # e.g.: [#NounChunk[#Noun '色'][#Subject 'は']][#AdjChunk[#Adj '濃'][#Base 'い']][#NounChunk[#Noun '赤']]

    
    return conv(tree[0])

  if tree == 'AdjChunk':
    # e.g.: [#AdjChunk[#Adjv '滑らか'][#Be 'な']]
    return conv(tree[0])
  if tree == 'VerbChunk':
    # e.g.: [#VerbChunk[#Verb1 '跳ね'][#Do 'る']]
    # e.g.: [#VerbChunk[#Verb1 '跳ね'][#DoNot 'ない']]    
    neg = False
    if tree[len(tree)-1] == 'DoNot' or tree[len(tree)-1] == 'DidNot':
      neg = True
    return Verb(conv(tree[0]), neg)

  if tree == 'NounChunk':
    # e.g.: [#NounChunk [#Noun '色'] [#Subject 'は']]
    return conv(tree[0])

  if tree == 'Noun':
    return str(tree)

  if tree == 'VerbKA':
    tree = str(tree) + 'く'
    return str(tree)
  if tree == 'VerbSA':
    tree = str(tree) + 'す'
    return str(tree)
  if tree == 'VerbTA':
    tree = str(tree) + 'つ'
    return str(tree)
  if tree == 'VerbNA':
    tree = str(tree) + 'ぬ'
    return str(tree)
  if tree == 'VerbMA':
    tree = str(tree) + 'む'
    return str(tree)
  if tree == 'VerbRA':
    tree = str(tree) + 'る'
    return str(tree)
  if tree == 'VerbWA':
    tree = str(tree) + 'う'
    return str(tree)
  if tree == 'VerbGA':
    tree = str(tree) + 'ぐ'
    return str(tree)
  if tree == 'VerbBA':
    tree = str(tree) + 'ぶ'
    return str(tree)
  if tree == 'Verb1':
    tree = str(tree) + 'る'
    return str(tree)

  # [TODO:] 修飾語の処理
  if tree == 'Adj':
    return str(tree)
  if tree == 'Adjv':
    return str(tree)
  if tree == 'Adverb':
    return str(tree)
  
e = conv(tree)
c = e.translate()
# c = e.emit()
print(c)