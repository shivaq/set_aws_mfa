# テスト
## 使い方

- 下記がPipfile に定義されている
- `execute` と実効すれば、実効できる

- ~/.bash_profile に下記のようにエイリアスを設定しておけば、pre で実行できる
```sh
# For pipenv
## use below with Pipfile scripts
alias pre="pipenv run execute"
alias prtc="pipenv run test"
```
```init
[scripts]
execute = "python3 -m set_aws_mfa"
```

```plantuml
@startuml
title Factory

interface Product {
  --
  + productMethod1
  + productMethod2
  + productMethod3
}

class ProductA {
  --
  + productMethod1
  + productMethod2
  + productMethod3
}

class ProductB {
  --
  + productMethod1
  + productMethod2
  + productMethod3
}

abstract class Creator {
  --
  # {abstract} factoryMethod(): Product
  + anOperation()
}

class CreatorA {
  --
  # factoryMethod(): Product
}

class CreatorB {
  --
  # factoryMethod(): Product
}

Creator <|-- CreatorA
Creator <|-- CreatorB
Product <|.. ProductA
Product <|.. ProductB
ProductA <. CreatorA : create
ProductB <. CreatorB : create
Product <. Creator : use


note right of Creator
  // anOperationの処理フローの例
  func anOperation() {
    product = this.factoryMethod()
    product.productMethod1
    product.productMethod2
    product.productMethod3
  }
end note
@enduml

```
