# 공통 헬퍼 메서드들
require 'fastlane'

module CommonHelper
  def self.setup_app_store_api_key(options)
    # App Store Connect API 키 설정을 위한 파라미터 반환
    {
      key_id: options[:api_key_id],           # API Key ID (10자리)
      issuer_id: options[:api_key_issuer_id], # Issuer ID (UUID 형식)
      key_filepath: options[:api_key_path]    # .p8 파일 경로
    }
  end

  def self.extract_build_info_from_ipa(options)
    # IPA 파일에서 빌드 정보 추출하여 로그에 출력
    return unless options[:ipa] && File.exist?(options[:ipa])

    Fastlane::UI.message "📱 Extracting build information from IPA..."
    
    begin
      # unzip 명령어를 사용해서 IPA에서 Info.plist 추출
      require 'tempfile'
      require 'fileutils'
      
      Dir.mktmpdir do |temp_dir|
        # IPA 압축 해제
        system("unzip -q '#{options[:ipa]}' -d '#{temp_dir}'")

        # Info.plist 파일 찾기
        info_plist_path = Dir.glob("#{temp_dir}/Payload/*/Info.plist").first
        
        if info_plist_path
          # plutil을 사용해서 Info.plist를 JSON으로 변환하여 읽기
          json_output = `plutil -convert json -o - '#{info_plist_path}' 2>/dev/null`
          
          if $?.success? && !json_output.empty?
            require 'json'
            info_plist = JSON.parse(json_output)
            
            version = info_plist['CFBundleShortVersionString']
            build_number = info_plist['CFBundleVersion']
            bundle_id = info_plist['CFBundleIdentifier']
          
            Fastlane::UI.important "🔍 Build Information:"
            Fastlane::UI.message "   📦 Bundle ID: #{bundle_id}"
            Fastlane::UI.message "   📱 App Version: #{version}"
            Fastlane::UI.message "   🔢 Build Number: #{build_number}"
            Fastlane::UI.message "   📝 Full Version: #{version} (#{build_number})"
          
            # 빌드 정보를 해시로 반환
            {
              bundle_id: bundle_id,
              version: version,
              build_number: build_number,
              full_version: "#{version} (#{build_number})"
            }
          else
            Fastlane::UI.message "⚠️  Could not parse Info.plist from IPA"
            nil
          end
        else
          Fastlane::UI.message "⚠️  Could not find Info.plist in IPA"
          nil
        end
      end
    rescue => e
      Fastlane::UI.message "⚠️  Could not extract build info from IPA: #{e.message}"
      nil
    end
  end

  def self.process_release_notes(options)
    # 릴리즈 노트 처리 로직
    # Available language codes
    # - ar-SA, ca, cs, da, de-DE, el, en-AU, en-CA, en-GB, en-US, es-ES, es-MX, fi, fr-CA, fr-FR, 
    # - he, hi, hr, hu, id, it, ja, ko, ms, nl-NL, no, pl, pt-BR, pt-PT, ro, ru, sk, sv, th, tr, 
    # - uk, vi, zh-Hans, zh-Hant
    # 방법 1: JSON 문자열로 전달 (예: '{"en-US":"English notes","ko":"Korean notes"}')
    # 방법 2: 콤마 구분 형식 (예: 'en-US:English notes,ko:Korean notes')
    # 방법 3: 파일 경로 (예: 'file:./release_notes.json')
    # 방법 4: 기본 문자열
    if options[:release_notes] && options[:release_notes].start_with?('file:')
      # 파일에서 읽기
      file_path = options[:release_notes].sub('file:', '')
      if File.exist?(file_path)
        file_content = File.read(file_path)
        if file_path.end_with?('.json')
          require 'json'
          JSON.parse(file_content)
        else
          file_content
        end
      else
        "Bug fixes and improvements"
      end
    elsif options[:release_notes] && options[:release_notes].start_with?('{')
      # JSON 형식으로 전달된 경우
      require 'json'
      parsed = JSON.parse(options[:release_notes])
      # \n을 실제 줄바꿈으로 변환
      parsed.transform_values { |v| v.gsub('\\n', "\n") }
    elsif options[:release_notes] && options[:release_notes].include?(':')
      # 콤마 구분 key:value 형식으로 전달된 경우
      notes_hash = {}
      options[:release_notes].split(',').each do |pair|
        key, value = pair.split(':', 2)
        if key && value
          # \n을 실제 줄바꿈으로 변환
          notes_hash[key.strip] = value.strip.gsub('\\n', "\n")
        end
      end
      notes_hash.empty? ? "Bug fixes and improvements" : notes_hash
    else
      # 기본 문자열 또는 nil인 경우
      notes = options[:release_notes] || "Bug fixes and improvements"
      notes.gsub('\\n', "\n")
    end
  end
    
  # Android metadata changelogs 폴더 생성 및 릴리즈 노트 파일 작성
  def self.create_android_metadata_changelogs(options)
    return unless options[:release_notes]
    
    Fastlane::UI.message "📝 Processing release notes..."
    Fastlane::UI.message "📝 Release notes data: #{options[:release_notes]} (#{options[:release_notes].class})"
    
    # JSON 문자열인 경우 파싱
    release_notes_data = options[:release_notes]
    if release_notes_data.is_a?(String)
      require 'json'
      release_notes_data = JSON.parse(release_notes_data)
    end
    
    # 버전 코드 가져오기
    version_code = "default"
    
    # metadata/android 폴더 생성
    metadata_dir = File.join(Dir.pwd, "metadata", "android")
    system("mkdir -p '#{metadata_dir}'")
    
    # 각 언어별로 폴더 생성 및 릴리즈 노트 파일 작성
    release_notes_data.each do |lang, note|
      # Android Play Store 언어 코드 매핑
      android_lang_code = map_to_android_language_code(lang.to_s)
      
      # metadata/android/{언어}/changelogs 폴더 생성
      changelogs_dir = File.join(metadata_dir, android_lang_code, "changelogs")
      system("mkdir -p '#{changelogs_dir}'")
      
      # 버전코드.txt 파일 생성
      release_note_file = File.join(changelogs_dir, "#{version_code}.txt")
      File.write(release_note_file, note)
      
      Fastlane::UI.success "✅ Created release note: #{release_note_file}"
      Fastlane::UI.message "   Content: #{note}"
    end
  end

  # iOS metadata release_notes.txt 파일 생성
  def self.create_ios_metadata_release_notes(options)
    return unless options[:release_notes]
    
    Fastlane::UI.message "📝 Processing iOS release notes..."
    Fastlane::UI.message "📝 Release notes data: #{options[:release_notes]} (#{options[:release_notes].class})"
    
    # JSON 문자열인 경우 파싱
    release_notes_data = options[:release_notes]
    if release_notes_data.is_a?(String)
      require 'json'
      release_notes_data = JSON.parse(release_notes_data)
    end
    
    # metadata 폴더 생성 (ios 하위폴더 없이)
    metadata_dir = File.join(Dir.pwd, "metadata")
    system("mkdir -p '#{metadata_dir}'")
    
    # 각 언어별로 폴더 생성 및 릴리즈 노트 파일 작성
    release_notes_data.each do |lang, note|
      # iOS App Store Connect 언어 코드 매핑
      ios_lang_code = map_to_ios_language_code(lang.to_s)
      
      # metadata/{언어} 폴더 생성
      lang_dir = File.join(metadata_dir, ios_lang_code)
      system("mkdir -p '#{lang_dir}'")
      
      # release_notes.txt 파일 생성
      release_note_file = File.join(lang_dir, "release_notes.txt")
      File.write(release_note_file, note)
      
      Fastlane::UI.success "✅ Created iOS release note: #{release_note_file}"
      Fastlane::UI.message "   Content: #{note}"
    end
  end
  
  # Android Play Store 언어 코드 매핑
  def self.map_to_android_language_code(lang)
    language_map = {
      'ko' => 'ko-KR',
      'en' => 'en-US',
      'ja' => 'ja-JP',
      'zh' => 'zh-CN',
      'zh-hans' => 'zh-CN',
      'zh-hant' => 'zh-TW',
      'es' => 'es-ES',
      'fr' => 'fr-FR',
      'de' => 'de-DE',
      'it' => 'it-IT',
      'pt' => 'pt-BR',
      'ru' => 'ru-RU',
      'ar' => 'ar-SA',
      'hi' => 'hi-IN',
      'th' => 'th-TH',
      'vi' => 'vi-VN',
      'tr' => 'tr-TR',
      'pl' => 'pl-PL',
      'nl' => 'nl-NL',
      'sv' => 'sv-SE',
      'da' => 'da-DK',
      'fi' => 'fi-FI',
      'no' => 'nb-NO',
      'cs' => 'cs-CZ',
      'sk' => 'sk-SK',
      'hu' => 'hu-HU',
      'ro' => 'ro-RO',
      'hr' => 'hr-HR',
      'uk' => 'uk-UA',
      'he' => 'he-IL',
      'el' => 'el-GR',
      'ca' => 'ca-ES',
      'id' => 'id-ID',
      'ms' => 'ms-MY'
    }
    
    # 매핑된 언어 코드가 있으면 사용, 없으면 원본 사용
    language_map[lang.downcase] || lang
  end
  
  # iOS App Store Connect 언어 코드 매핑
  def self.map_to_ios_language_code(lang)
    language_map = {
      'ko' => 'ko',
      'en' => 'en-US',
      'ja' => 'ja',
      'zh' => 'zh-Hans',
      'zh-hans' => 'zh-Hans',
      'zh-hant' => 'zh-Hant',
      'es' => 'es-ES',
      'fr' => 'fr-FR',
      'de' => 'de-DE',
      'it' => 'it',
      'pt' => 'pt-BR',
      'pt-pt' => 'pt-PT',
      'ru' => 'ru',
      'ar' => 'ar-SA',
      'hi' => 'hi',
      'th' => 'th',
      'vi' => 'vi',
      'tr' => 'tr',
      'pl' => 'pl',
      'nl' => 'nl-NL',
      'sv' => 'sv',
      'da' => 'da',
      'fi' => 'fi',
      'no' => 'no',
      'cs' => 'cs',
      'sk' => 'sk',
      'hu' => 'hu',
      'ro' => 'ro',
      'hr' => 'hr',
      'uk' => 'uk',
      'he' => 'he',
      'el' => 'el',
      'ca' => 'ca',
      'id' => 'id',
      'ms' => 'ms',
      'en-au' => 'en-AU',
      'en-ca' => 'en-CA',
      'en-gb' => 'en-GB',
      'es-mx' => 'es-MX',
      'fr-ca' => 'fr-CA'
    }
    
    # 매핑된 언어 코드가 있으면 사용, 없으면 원본 사용
    language_map[lang.downcase] || lang
  end
end
