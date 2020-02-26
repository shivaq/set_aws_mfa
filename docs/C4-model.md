# set_aws_mfa システム

## set_aws_mfa システム 【システムコンテキスト図】

```plantuml
@startuml
!includeurl https://raw.githubusercontent.com/RicardoNiepel/C4-PlantUML/master/C4_Context.puml

title set_aws_mfa システム 【システムコンテキスト図】


'ユーザー'
Person(developer, "AWSを使う開発者", "AWS CLI を使って、AWSサービスを利用する")

'対象システム'
System(set_aws_mfa, "AWS の MFA トークンをセットするシステム", "ローカル端末に格納されているAWS のユーザー情報、credentials、MFAトークンを使って aws cli を使う際の認証を行う")

'外部システム'
System_Ext(iam, "IAM認証システム", "IAMユーザーの認証を行う")
System_Ext(Authy, "2FA codes generator", "認証コードを生成する")
System_Ext(aws_cli, "aws cli", "AWS のリソースを操作する CLI")

'関係性'
Rel(developer, set_aws_mfa, "Uses")
Rel_Back(developer, Authy, "Read from")
Rel_Back(developer, aws_cli, "Uses")

Rel(set_aws_mfa, iam, "Uses", 'Assumerole')
@enduml
```

## set_aws_mfa システム 【コンテナ図】

```plantuml
@startuml
!includeurl https://raw.githubusercontent.com/RicardoNiepel/C4-PlantUML/master/C4_Container.puml


title set_aws_mfa システム 【コンテナ図】

'ユーザー'
Person(developer, "AWSを使う開発者", "AWS CLI を使って、AWSサービスを利用する")

System_Boundary(c1, "set_aws_mfa") {
    Container(set_aws_mfa, "set_aws_mfa", "python3.7", "Orchestrate retrieving aws config, credentials, aws mfa token and authenticate to access aws account with aws cli")

    ContainerDb(config, "aws config", "ini file", "Stores profile name, region, role arn, source profile for a role")
    ContainerDb(credentials, "aws credentials", "ini file", "Stores aws_access_key_id, aws_secret_access_key")
}

'外部システム'
System_Ext(iam, "IAM認証システム", "IAMユーザーの認証を行う")
System_Ext(Authy, "2FA codes generator", "認証コードを生成する")
System_Ext(aws_cli, "aws cli", "AWS のリソースを操作する CLI")

Rel(developer, set_aws_mfa, "Uses")

Rel(set_aws_mfa, config, "Reads from", "config settings")
Rel(set_aws_mfa, credentials, "Reads from", "credentials")
Rel_Back(developer, Authy, "Read from")
Rel(set_aws_mfa, iam, "Autehenticate", "iam user")
Rel(set_aws_mfa, aws_cli, "Uses", "AWS resources")


@enduml
```

## set_aws_mfa システム 【コンポーネント図】

```plantuml
@startuml
!includeurl https://raw.githubusercontent.com/RicardoNiepel/C4-PlantUML/master/C4_Component.puml



title set_aws_mfa システム 【コンポーネント図】



Container_Boundary(set_aws_mfa, "認証 ユーティリティ") {
    Component(set_aws_mfa_module, "set_aws_mfa", "python3.7", "Orchestrate retrieving aws config, credentials, aws mfa token and authenticate to access aws account with aws cli")


}

    ContainerDb(config, "aws config", "ini file", "Stores profile name, region, role arn, source profile for a role")
    ContainerDb(credentials, "aws credentials", "ini file", "Stores aws_access_key_id, aws_secret_access_key")


Rel_D(set_aws_mfa, config, "Reads from", "config settings")
Rel_D(set_aws_mfa, credentials, "Reads from", "credentials")

@enduml
```
