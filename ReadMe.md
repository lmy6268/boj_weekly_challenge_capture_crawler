## 개발 배경 
진행하고 있는 스터디에서 과제 제출 시, 일일히 화면을 캡쳐해야하는 번거로움이 있어 해결하고자 개발하게 되었습니다.

## 개발 환경
Python 3.9.6 / Macbook Pro M2 Pro (MacOS 14.4.1) / Chrome 124.0.6367.62 

## 사용한 라이브러리
Selenium, OpenCV, Pillow

## 사용 방법 
1. 프로그램 실행을 위해, 크롬이 설치되어 있어야 합니다.
   - 만약 설치되어 있지 않으시다면, [링크](https://www.google.com/chrome/) 를 통해 설치해 주시고 2번을 진행해주세요. 

2. 터미널(또는 CMD)를 실행하시고, main.py가 위치한 폴더로 이동해주세요. 

3. 이 프로그램은 Python 3.9버전에 최적화 되어있습니다.
   <br>
   다양한 버전을 사용할 수 있는 파이썬 환경 상, 가상환경을 통해 진행해 주시길 권장합니다. 
   <br>
   <details>
      <summary>Windows 사용자</summary>
   
   >  [블로그](https://idenrai.tistory.com/277)를 참고하여 작성되었습니다 
   1. PowerShell을 관리자 모드로 실행합니다. 
   2. pyenv를 설치합니다.
      ```powershell
      pip install pyenv-win --target $HOME\.pyenv
      ```
   3. 환경 변수를 설정해줍니다.
      > 다음을 순서대로 입력해줍니다. 
      
      ```powershell
      [System.Environment]::SetEnvironmentVariable('PYENV',$env:USERPROFILE + "\.pyenv\pyenv-win\","User")
      ``` 
      ```powershell
      [System.Environment]::SetEnvironmentVariable('PYENV_ROOT',$env:USERPROFILE + "\.pyenv\pyenv-win\","User")
      ``` 
      ```powershell
      [System.Environment]::SetEnvironmentVariable('PYENV_HOME',$env:USERPROFILE + "\.pyenv\pyenv-win\","User")
      ``` 
      ```powershell
      [System.Environment]::SetEnvironmentVariable('path', $env:USERPROFILE + "\.pyenv\pyenv-win\bin;" + $env:USERPROFILE + "\.pyenv\pyenv-win\shims;" + [System.Environment]::GetEnvironmentVariable('path', "User"),"User")
      ``` 
   4. PowerShell을 종료 후 다시 관리자모드로 실행합니다.
   5. 정상적으로 작동하는지 확인합니다.
      ```powershell
      pyenv --version
      ```
   6. 설치가 완료되면, 가상환경에서 설치할 3.9.6버전을 다음 명령어를 이용해 받아줍니다. 
      ```shell
      pyenv install 3.9.6
      ```
   7.  `main.py`가 있는 위치로 이동합니다. 
   8. 현재 폴더에만 특정 파이썬 버전을 기본으로 사용하도록 지정합니다. 
      ```shell
      python local 3.9.6
      ```
         
   9.  `pyenv rehash` 를 입력하여, 변경사항을 시스템에 반영합니다. 
   10. 파이썬 가상개발 환경을 생성합니다.
         ```shell
         python -m venv env
         ```
   11. 가상환경을 실행합니다. 
         ```shell
         env\Scripts\activate
         ```
          - 종료는 다음과 같이 진행합니다. 
             ```shell
             deactivate
             ```
   </details>

   <details>
   <summary>MAC OS 사용자</summary>

      > [블로그](https://junkwon-dev.github.io/python/python-pyenv/) 를 참고하여 작성되었습니다. 

   1. 터미널을 실행해주세요. 
   2. HomeBrew를 설치해 주세요. ( 이미 설치된 경우 3번 진행 )
         ```bash 
         $ /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
         ```
      - 설치 후, 올바른 적용을 위해 터미널을 종료하신 후 다시 실행해주세요.   
  
   3.  `brew install pyenv` 를 통해, pyenv를 설치해줍니다.
   4.  환경 변수를 설정해줍니다.
         ``` bash
            $ echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
            $ echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zhsrc
            $ echo 'eval "$(pyenv init -)"' >> ~/.zshrc
            $ source ~/.zshrc
         ```
       * bash터미널을 사용한다면 끝에 ~/.zshrc를 ~/.bash_profile 로 바꾸어 주세요. 
   5.  가상개발환경을 만들기 위해, virtualenv 를 설치합니다.
   
         ```bash
         $ brew install pyenv-virtualenv

         $ echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.zshrc
         $ source ~/.zshrc
         ```
    
   6.  pyenv에 파이썬 3.9.6 버전을 설치하고, 해당 버전을 이용한 가상 개발환경을 만듭니다. 
         ```bash
         $ pyenv install 3.9.6 #pyenv에 파이썬 3.9.6버전 설치

         $ pyenv virtualenv 3.9.6 web_crawler_venv #가상환경 생성
         $ pyenv versions # 잘 추가되었는지 확인한다.
         ```
   7.  `main.py`가 있는 폴더로 이동합니다. 
   8.  가상 개발 환경을 현재 폴더에 적용합니다. 
         ```zsh
         $ pyenv local web_crawler_venv
         ```
   9.  터미널을 종료 후 다시 실행하면, 다음과 같이 나타나며, 가상환경이 **실행됨**을 확인할 수 있습니다. 
         ```zsh
         (web_crawler_venv)  ~
         ```
   
   </details>

   
5. 터미널 창에서 `pip install -r requirements.txt` 또는 `pip3 install -r requirements.txt`을 입력하여, 필요한 라이브러리를 설치해주세요. 

6. 설치가 완료된 후,  터미널에서  `python3 "./main.py"` 또는 `python "./main.py"` 을 입력하여, 파일을 실행해주세요. 


7. 사용자의 이름과 백준 아이디를 입력하신 후, 약 5~10초 정도 기다려주세요.
   - **프로그램 첫 실행 시, 백준 로그인이 필요합니다. (이후 해당 로그인 정보 세션을 로컬에 저장하여,이를 이용하도록 구성하였습니다.)**
   - 그룹 내 연습 문제 정보를 얻기 위해 로그인을 필요로 하게 되었습니다.


8. 이후, 결과 이미지가 화면에 나타나고, 이미지가 저장된 경로가 터미널에 나타납니다.

## 예시 이미지 
![이미지](https://github.com/lmy6268/boj_weekly_challenge_capture_crawler/assets/70847610/f715bfc3-71e1-4300-9b1a-1983daf77fe5)
