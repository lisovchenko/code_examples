class CommunityLocalMiddleware(LocaleMiddleware):
   def process_request(self, request):
       language = translation.get_language_from_request(
           request, check_path=self.is_language_prefix_patterns_used)
       language = self.get_community_language_from_request(request, language)
       translation.activate(language)
       request.LANGUAGE_CODE = translation.get_language()

   @staticmethod
   def get_community_language_from_request(request, lang_code):
       """Check if we have localization for this community.

       We get from the request tenant, build a community language for it.
       We check if we have localization for community language.
       If exists we are return a new community language,
       else, we are return the default one.
       """
       community = request.tenant
       supported_lang_codes = get_languages()
       community_lang = community_language(community, lang_code)

       if all([
           community_lang in supported_lang_codes,
           community_lang is not None,
           check_for_community_language(community_lang)
       ]):
           return community_lang
       return lang_code


@lru_cache.lru_cache(maxsize=1000)
def check_for_community_language(lang_code):
   """Checks whether there is a language file for the given language code.

   lru_cache should have a maxsize to prevent from memory exhaustion attacks,
   as the provided language codes are taken from the HTTP request. See also
   <https://www.djangoproject.com/weblog/2007/oct/26/security-fix/>.
   """
   if lang_code is None:
       return False
   for path in locale_paths():
       if gettext_module.find('django', path, [lang_code]) is not None:
           return True
   return False


def locale_paths():
   return list(settings.LOCALE_PATHS)


def community_language(community, lang_code):
   normalize_schema = schema_re.sub('', community.schema_name)
   community_lang = '{lang_code}_{schema}'.format(
       schema=normalize_schema,
       lang_code=lang_code
   )
   return community_lang
