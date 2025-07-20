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

  def self.extract_build_info_from_ipa(ipa_path)
    # IPA 파일에서 빌드 정보 추출하여 로그에 출력
    return unless ipa_path && File.exist?(ipa_path)
    
    Fastlane::UI.message "📱 Extracting build information from IPA..."
    
    begin
      # unzip 명령어를 사용해서 IPA에서 Info.plist 추출
      require 'tempfile'
      require 'fileutils'
      
      Dir.mktmpdir do |temp_dir|
        # IPA 압축 해제
        system("unzip -q '#{ipa_path}' -d '#{temp_dir}'")
        
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

  def self.extract_build_info_from_apk(apk_path)
    # APK 파일에서 빌드 정보 추출하여 로그에 출력
    return unless apk_path && File.exist?(apk_path)
    
    Fastlane::UI.message "📱 Extracting build information from APK..."
    
    begin
      # aapt를 사용해서 APK에서 정보 추출
      output = `aapt dump badging '#{apk_path}' 2>/dev/null`
      
      if $?.success? && !output.empty?
        # package 정보 추출
        package_match = output.match(/package: name='([^']+)'.*versionCode='([^']+)'.*versionName='([^']+)'/)
        
        if package_match
          package_name = package_match[1]
          version_code = package_match[2]
          version_name = package_match[3]
          
          Fastlane::UI.important "🔍 Build Information:"
          Fastlane::UI.message "   📦 Package Name: #{package_name}"
          Fastlane::UI.message "   📱 App Version: #{version_name}"
          Fastlane::UI.message "   🔢 Version Code: #{version_code}"
          Fastlane::UI.message "   📝 Full Version: #{version_name} (#{version_code})"
          
          # 빌드 정보를 해시로 반환
          {
            package_name: package_name,
            version_name: version_name,
            version_code: version_code,
            full_version: "#{version_name} (#{version_code})"
          }
        else
          Fastlane::UI.message "⚠️  Could not parse package info from APK"
          nil
        end
      else
        Fastlane::UI.message "⚠️  Could not read APK file with aapt"
        nil
      end
    rescue => e
      Fastlane::UI.message "⚠️  Could not extract build info from APK: #{e.message}"
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
end
