import pathlib as Path
import pegpy
#from pegpy.tpeg import ParseTree
peg = pegpy.grammar('cj.tpeg')
parser = pegpy.generate(peg)

tree = parser('静止する')
# print(repr(tree))
print('@debug(input): ', list(tree))

# value の推論update
# @debug(input):  [[#NounChunk [#Noun '固定']]]
# 形容詞副詞まわり

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
             '青': '#0095d9',
             '白': '#ffffff',
             '緑': '#3eb370',
             '黒': '#2b2b2b',
             '紫': '#884898',
             '黄緑': '#b8d200',
             '桜色': '#fef4f4',
             '桃色': '#f09199',
             '褐色': '#4d4c61',
             '水色': '#bce2e8',
             '紺色': '#223a70',
             '橙色': '#ee7800',
             '肌色': '#fce2c4',
             '黄色': '#ffd900',
             '灰色': '#7d7d7d',
             '金色': '#e6b422',
             'レッド': '#ea5550',
             'ホワイト': '#ffffff',
             'クリーム': '#e3d7a3',
             'アイボリー': '#f8f4e6',
             'イエロー': '#ffdc00',
             'パープル': '#9b72b0',
             'ブラウン': '#8f6552',
             'シアン': '#00a1e9',
             'マゼンタ': '#e4007f',
             'シルバー': '#c9caca',
             'オレンジ': '#ee7800',
             'ブルー': '#0075c2',
             'グリーン': '#00a960',
             'グレイ': '#7d7d7d',
             'ベージュ': '#eedcb3',
             'ブラック': '#000000',
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
      sim_key_max = 0.0
      sim_key = None
      for word in list(property.keys()):
        sim = model.similarity(word, self.left)
        if sim > sim_key_max:
          sim_key_max = sim
          sim_key = word
      key = property[sim_key]

    if key == 'fillStyle':
      if self.right in fillStyle:
        value = fillStyle[self.right]
      else:
        from gensim.models import KeyedVectors
        model = KeyedVectors.load_word2vec_format(model_dir, binary=True)
        if self.right not in model:
          return None
        sim_value_max = 0.0
        sim_value = None
        for word in list(fillStyle.keys()):
          sim = model.similarity(word, self.right)
          if sim > sim_value_max:
            sim_value_max = sim
            sim_value = word
        print('@debug(sim_value): ', sim_value)
        print('@debug(sim_value_max): ', sim_value_max)
        value = fillStyle[sim_value]
    
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
      print('@debug(key): ', key)

    if key == 'restitution':
      if self.neg == True:
        value = restitution['neg']
      else:
        value = restitution['pos']

    value = 'xxx'

    return key, value

  # def emit(self):
  #   return f'{self.value}'

# e = Verb('書く')
# isinstance(e, Verb) # 種類
# translate


def conv(tree) :
  if tree == 'S':
    print('@debug(str): ', str(tree))

    # Chunk の組み合わせ
    if len(tree) > 1:
      if tree[0] == 'NounChunk' and tree[-1] == 'NounChunk':
        left = tree[0]
        right = tree[-1]
        return Let(conv(left[0]), str(right))

      if tree[0] == 'Adverb' and tree[1] == 'VerbChunk':
        # e.g.: [#Adverb 'よく'][#VerbChunk[#Verb1 '跳ね'][#Do 'る']]
        # e.g.: [#Adverb '全く'][#VerbChunk[#Verb1 '跳ね'][#DoNot 'ない']]
        # e.g.: [#Adverb 'あまり'][#VerbChunk[#Verb1 '跳ね'][#DoNot 'ない']]

        return 0

    # e.g.: [#NounChunk[#Noun '色'][#Subject 'は']][#AdjChunk[#Adj '濃'][#Base 'い']][#NounChunk[#Noun '赤']]

    return conv(tree[0])


  # Chunk 単体
  if tree == 'AdjChunk':
    # e.g.: [#AdjChunk[#Adjv '滑らか'][#Be 'な']]
    return conv(tree[0])

  if tree == 'VerbChunk':
    # e.g.: [#VerbChunk[#Verb1 '跳ね'][#Do 'る']]
    # e.g.: [#VerbChunk[#Verb1 '跳ね'][#DoNot 'ない']]    
    neg = False
    if tree[-1] == 'DoNot' or tree[-1] == 'DidNot':
      neg = True
    return Verb(conv(tree[0]), neg)

  if tree == 'NounChunk':
    # e.g.: [#NounChunk [#Noun '色'] [#Subject 'は']]
    return conv(tree[0])


  # 品詞
  if tree == 'Adj':
    return str(tree)
  if tree == 'Adjv':
    return str(tree)
  if tree == 'Adverb':
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

  if tree == 'Noun':
    return str(tree)
    # return Verb(str(tree), neg=Fals1e)

  
e = conv(tree)
c = e.translate()
# c = e.emit()
print(c)