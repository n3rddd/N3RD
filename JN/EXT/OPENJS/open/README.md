## Support using private Gitee or GitHub repositories as remote config.
    * github://<your personal access token>@github.com/<owner>/<repo>/<ref>/<file path>
    * gitee://<your access token>@gitee.com/<owner>/<repo>/<ref>/<file path>
    * github://ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx@github.com/catvod/TestCfg/main/config_open.json
    * gitee://xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx@gitee.com/catvod/test-cfg/master/config_open.json


## personal access token
    * Settings > Developer settings > Personal access tokens > Token (classic) > Generate new token
    * Settings > Developer settings > Personal access tokens > Fine-grained tokens > Generate new token


## 远端配置：
    * github://ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx@github.com/YuanHsing/CatVodOpen/main/js/config_open2.json
    * github://github_pat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx@github.com/YuanHsing/CatVodOpen/main/js/config_open2.json


## 本地配置：
    * assets://js/config_open.json

## 参考教程：
    * https://omii.top/1296.html

## 添加格式：
      {
                "key": "pan99",  
                "name": "🟢 盘九",
                "type": 3,
                "api": "./pan99_open.js",
                "ext": "填入阿里token"
            },
            
      //"key"、"name" 内:与其他不重复的名称均可。     
     //"type" 3为影视，10为有声读物
    //"api" 填写js路径，"ext" 填写扩展内容，例如玩偶的token。
