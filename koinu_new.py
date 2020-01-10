import pathlib as Path
import pegpy
#from pegpy.tpeg import ParseTree
peg = pegpy.grammar('cj.tpeg')
parser = pegpy.generate(peg)
model_dir = 'nlp_dict/entity_vector.model.bin'

tree = parser('跳ねている')
# print(repr(tree))
print('@debug(input): ', list(tree))

# 赤と赤色（赤は赤でマッピング、赤色だと黄色でマッピング）

degree_dict = {'たいして': 'little',
               'さほど': 'little',
               'あまり': 'little',
               'そんなに': 'little',
               'ちっとも': 'neg',
               '少しも': 'neg',
               '全然': 'neg',
               '全く': 'neg',
               '決して': 'neg',

               'よく': 'more',
               'かなり': 'more',
               'けっこう': 'more',
               '相当': 'more',
               'めちゃくちゃ': 'more',
               'めっちゃ': 'more',
               '少し': 'little',
               'ちょっぴり': 'little',
               'ちょっと': 'little',
               'たくさん': 'more',
               'いっぱい': 'more',
               'たっぷり': 'more'}

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
            # '摩擦': 'friction',
            # '空気摩擦': 'frictionAir',         # モデル登録なし
            # '静止摩擦力': 'frictionStatic',    # モデル登録なし
            # 'センサー': 'isSensor',
            '固定': 'isStatic',
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

# angle = {}

# friction = {'pos': '0.001',
#             'neg': '0.0000001'}

isStatic = {'pos': 'True',
            'neg': 'False'}

restitution = {'more': '1.2',
               'pos': '1.0',
               'little': '0.7',
               'neg': '0.0'}


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

    if key == 'restitution':
      try:
        value = float(self.right)
      except:
        value = 1.0
      value = str(value)
    
    return key, value

  # def emit(self):
  #   self.translate(self)
  #   return f'{self.key} = {self.value}'
  #   return f'{key} = {self.right}'


class Verb(Expr):
  key: str
  value: str
  def __init__(self, domain: str, flag_neg: bool, degree: str):
    self.domain = domain
    self.flag_neg = flag_neg
    self.degree = degree

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
      # print('@debug(key): ', key)

    if key == 'fillStyle':
      if self.domain in fillStyle:
        value = fillStyle[self.domain]
      else:
        from gensim.models import KeyedVectors
        model = KeyedVectors.load_word2vec_format(model_dir, binary=True)
        if self.domain not in model:
          return None
        sim_value_max = 0.0
        sim_value = None
        for word in list(fillStyle.keys()):
          sim = model.similarity(word, self.domain)
          if sim > sim_value_max:
            sim_value_max = sim
            sim_value = word
        print('@debug(sim_value): ', sim_value)
        print('@debug(sim_value_max): ', sim_value_max)
        value = fillStyle[sim_value]

    if key == 'restitution':
      if self.flag_neg:
        value = restitution['neg']
        if self.degree == 'little':
          value = restitution['little']
      else:
        value = restitution['pos']
        if self.degree == 'little':
          value = restitution['little']
        if self.degree == 'more':
          value = restitution['more']

    if key == 'isStatic':
      if self.flag_neg:
        value = isStatic['neg']
      else:
        value = isStatic['pos']

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

      if tree[0] == 'Adverb' and tree[-1] == 'VerbChunk':
        # e.g.: [#Adverb 'よく'][#VerbChunk[#Verb1 '跳ね'][#Do 'る']]
        # e.g.: [#Adverb '全く'][#VerbChunk[#Verb1 '跳ね'][#DoNot 'ない']]
        # e.g.: [#Adverb 'あまり'][#VerbChunk[#Verb1 '跳ね'][#DoNot 'ない']]
        degree = 'pos'
        if str(tree[0]) in degree_dict:
          degree = degree_dict[str(tree[0])]

        tree = tree[-1]
        flag_neg = 0
        if tree[-1] == 'DoNot' or tree[-1] == 'DidNot':
          flag_neg = 1
        
        return Verb(conv(tree[0]), flag_neg, degree)

    # !!!e.g.: [#NounChunk[#Noun '色'][#Subject 'は']][#AdjChunk[#Adj '濃'][#Base 'い']][#NounChunk[#Noun '赤']]

    return conv(tree[0])


  # Chunk 単体
  if tree == 'AdjChunk':
    # e.g.: [#AdjChunk[#Adjv '滑らか'][#Be 'な']]
    return conv(tree[0])

  if tree == 'VerbChunk':
    # e.g.: [#VerbChunk[#Verb1 '跳ね'][#Do 'る']]
    # e.g.: [#VerbChunk[#Verb1 '跳ね'][#DoNot 'ない']] 
    flag_neg = 0
    if tree[-1] == 'DoNot' or tree[-1] == 'DidNot':
      flag_neg = 1
    
    return Verb(conv(tree[0]), flag_neg, degree='pos')

  if tree == 'NounChunk':
    # e.g.: [#NounChunk [#Noun '色'] [#Subject 'は']]
    if tree[-1] == 'Noun':
      return Verb(str(tree[-1]), flag_neg=0, degree='pos')
    return conv(tree[0])


  # 品詞
  if tree == 'Adj':
    return Verb(str(tree), flag_neg=0, degree='pos')
  if tree == 'Adjv':
    return Verb(str(tree), flag_neg=0, degree='pos')
  if tree == 'Adverb':
    return Verb(str(tree), flag_neg=0, degree='pos')

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

  if tree == 'err':
    return None

  
e = conv(tree)
c = e.translate()
# c = e.emit()
print(c)