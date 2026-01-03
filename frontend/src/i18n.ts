export const LANGS = ['Latvian', 'English', 'Spanish', 'Russian'] as const
export type Lang = (typeof LANGS)[number]

type DictionaryEntry = {
  appTitle: string
  appSubtitle: string
  navUpload: string
  navLibrary: string
  libraryTitle: string
  uploadTitle: string
  languageLabel: string
  chooseText: string
  choosePart: string
  fragmentHeading: string
  questionHeading: string
  answerPlaceholder: string
  submitButton: string
  readAgain: string
  regenerateEasy: string
  regenerateDefault: string
  strictnessLabel: string
  strictness: [string, string, string]
  audioFragment: string
  audioQuestion: string
  uppercase: string
  difficultyLabel: string
  fragmentToolsTitle: string
  fragmentSize: [string, string, string]
  fragmentPreview: string
  simplifyTitle: string
  simplifyGentle: string
  simplifyGentleHint: string
  simplifyDeep: string
  simplifyDeepHint: string
  formatButton: string
  formatButtonHint: string
  saveButton: string
  pastePlaceholder: string
  uploadSuccess: string
  uploadError: string
  previewHeading: string
  previewHint: string
  noQuestions: string
  questionHint: string
  modeLabel: string
  modeOriginal: string
  modeSimple: string
  toolsLabel: string
  toolRuler: string
  toolSize: string
  sizeNormal: string
  sizeLarge: string
  questionTitle: string
  answerLabel: string
  storyAudio: string
  storyAudioLoading: string
  storyAudioError: string
  resultLabel: string
  resultEmpty: string
  regenerateQuestionsLoading: string
  nextQuestion: string
  titleLabel: string
  titlePlaceholder: string
  storyCompleted: string
  correctAnswers: string
  startOver: string
  textLoadedSuccessfully: string
  fragmentScore: string
  finalScore: string
  generateAllQuestions: string
  generatingAllQuestions: string
  questionsGenerated: string
}

const dictionary: Record<Lang, DictionaryEntry> = {
  English: {
    appTitle: 'Reading Coach',
    appSubtitle: 'Upload your text, simplify it, and practise comprehension with instant feedback.',
    navUpload: '📤 Upload your text',
    navLibrary: 'Library',
    libraryTitle: '📚 Read Library Samples',
    uploadTitle: '📝 Upload Your Own Text',
    languageLabel: 'Language',
    chooseText: 'Choose a text…',
    choosePart: 'Choose a part…',
    fragmentHeading: 'Story fragment',
    questionHeading: 'Question',
    answerPlaceholder: 'Type your answer…',
    submitButton: 'Submit answer',
    readAgain: 'Read again & new questions',
    regenerateEasy: 'Easier questions',
    regenerateDefault: 'Standard questions',
    strictnessLabel: 'Evaluation strictness',
    strictness: ['Gentle', 'Balanced', 'Strict'],
    audioFragment: 'Listen fragment',
    audioQuestion: 'Listen question',
    uppercase: 'TO UPPERCASE',
    difficultyLabel: 'Question style',
    fragmentToolsTitle: 'Fragment tools',
    fragmentSize: ['Short', 'Standard', 'Long'],
    fragmentPreview: 'Preview fragments',
    simplifyTitle: 'Simplify level',
    simplifyGentle: 'Simplify text a little',
    simplifyGentleHint: 'Makes the text slightly easier to read while keeping most details',
    simplifyDeep: 'Simplify text more',
    simplifyDeepHint: 'Makes the text much simpler, using basic vocabulary and shorter sentences',
    formatButton: 'Clean up formatting',
    formatButtonHint: 'Fixes line breaks, spacing, and paragraph structure',
    saveButton: 'Save to library',
    pastePlaceholder: 'Paste or type your story here…',
    uploadSuccess: 'Story added to your library!',
    uploadError: 'Upload failed. Please try again.',
    previewHeading: 'Fragment preview',
    previewHint: 'Check how your text will be split into reading sections.',
    noQuestions: 'No questions yet. Click a button below to generate questions.',
    questionHint: 'Choose "Easier questions" if the current ones are too hard.',
    modeLabel: 'Mode',
    modeOriginal: 'Original',
    modeSimple: 'Simplified',
    toolsLabel: 'Tools',
    toolRuler: 'Ruler',
    toolSize: 'Size',
    sizeNormal: 'Normal',
    sizeLarge: 'Large',
    questionTitle: 'Question',
    answerLabel: 'Your answer',
    storyAudio: 'Listen to story',
    storyAudioLoading: 'Generating audio…',
    storyAudioError: 'Could not generate audio. Please try again.',
    resultLabel: 'Result',
    resultEmpty: 'Answer to see feedback here.',
    regenerateQuestionsLoading: 'Generating new questions…',
    nextQuestion: 'Next question',
    titleLabel: 'Title (optional)',
    titlePlaceholder: 'Leave empty to auto-generate from first words',
    storyCompleted: '🎉 Story Completed!',
    correctAnswers: 'Correct Answers',
    startOver: 'Start Over',
    textLoadedSuccessfully: '✅ Text loaded successfully:',
    fragmentScore: 'Fragment Score',
    finalScore: 'Final Score:',
    generateAllQuestions: 'Generate All Questions',
    generatingAllQuestions: 'Generating questions for all fragments...',
    questionsGenerated: 'Questions generated for all fragments!',
  },
  Latvian: {
    appTitle: 'Lasīšanas treneris',
    appSubtitle: 'Augšupielādē tekstu, vienkāršo to un trenē lasītprasmi ar tūlītēju atgriezenisko saiti.',
    navUpload: '📤 Augšupielādēt tekstu',
    navLibrary: 'Bibliotēka',
    libraryTitle: '📚 Bibliotēkas paraugi',
    uploadTitle: '📝 Augšupielādē savu tekstu',
    languageLabel: 'Valoda',
    chooseText: 'Izvēlies tekstu…',
    choosePart: 'Izvēlies daļu…',
    fragmentHeading: 'Stāsta fragments',
    questionHeading: 'Jautājums',
    answerPlaceholder: 'Ieraksti savu atbildi…',
    submitButton: 'Iesniegt atbildi',
    readAgain: 'Lasīt vēlreiz un jauni jautājumi',
    regenerateEasy: 'Vieglāki jautājumi',
    regenerateDefault: 'Parasti jautājumi',
    strictnessLabel: 'Vērtēšanas stingrība',
    strictness: ['Saudzīgi', 'Līdzsvaroti', 'Stingri'],
    audioFragment: 'Noklausīties fragmentu',
    audioQuestion: 'Noklausīties jautājumu',
    uppercase: 'LIELIE BURTI',
    difficultyLabel: 'Jautājumu stils',
    fragmentToolsTitle: 'Fragmenta rīki',
    fragmentSize: ['Īsi', 'Vidēji', 'Gari'],
    fragmentPreview: 'Skatīt fragmentus',
    simplifyTitle: 'Vienkāršošanas līmenis',
    simplifyGentle: 'Vienkāršot tekstu mazliet',
    simplifyGentleHint: 'Padara tekstu nedaudz vieglāk lasāmu, saglabājot lielāko daļu detaļu',
    simplifyDeep: 'Vienkāršot tekstu vairāk',
    simplifyDeepHint: 'Padara tekstu daudz vienkāršāku, izmantojot pamata vārdu krājumu un īsākus teikumus',
    formatButton: 'Sakārtot formatējumu',
    formatButtonHint: 'Labo rindas pārtraukumus, atstarpes un rindkopu struktūru',
    saveButton: 'Saglabāt bibliotēkā',
    pastePlaceholder: 'Ielīmē vai ieraksti stāstu…',
    uploadSuccess: 'Stāsts pievienots tavai bibliotēkai!',
    uploadError: 'Neizdevās augšupielāde. Pamēģini vēlreiz.',
    previewHeading: 'Fragmentu priekšskatījums',
    previewHint: 'Pārbaudi, kā tavs teksts tiks sadalīts lasīšanas daļās.',
    noQuestions: 'Jautājumi vēl nav izveidoti. Spied pogu, lai ģenerētu jautājumus.',
    questionHint: 'Izvēlies "Vieglāki jautājumi", ja pašreizējie ir pārāk grūti.',
    modeLabel: 'Režīms',
    modeOriginal: 'Oriģināls',
    modeSimple: 'Vienkāršots',
    toolsLabel: 'Rīki',
    toolRuler: 'Rindas',
    toolSize: 'Izmērs',
    sizeNormal: 'Standarts',
    sizeLarge: 'Liels',
    questionTitle: 'Jautājums',
    answerLabel: 'Tava atbilde',
    storyAudio: 'Klausīties stāstu',
    storyAudioLoading: 'Ģenerē audio…',
    storyAudioError: 'Neizdevās ģenerēt audio. Lūdzu, mēģini vēlreiz.',
    resultLabel: 'Rezultāts',
    resultEmpty: 'Atbildi, lai šeit redzētu atsauksmi.',
    regenerateQuestionsLoading: 'Ģenerē jaunus jautājumus…',
    nextQuestion: 'Nākamais jautājums',
    titleLabel: 'Nosaukums (neobligāts)',
    titlePlaceholder: 'Atstāj tukšu, lai automātiski ģenerētu no pirmajiem vārdiem',
    storyCompleted: '🎉 Stāsts pabeigts!',
    correctAnswers: 'Pareizās atbildes',
    startOver: 'Sākt no sākuma',
    textLoadedSuccessfully: '✅ Teksts ielādēts veiksmīgi:',
    fragmentScore: 'Fragmenta rezultāts',
    finalScore: 'Gala rezultāts:',
    generateAllQuestions: 'Ģenerēt visus jautājumus',
    generatingAllQuestions: 'Ģenerē jautājumus visiem fragmentiem...',
    questionsGenerated: 'Jautājumi ģenerēti visiem fragmentiem!',
  },
  Spanish: {
    appTitle: 'Entrenador de Lectura',
    appSubtitle: 'Sube tu texto, simplifícalo y practica la comprensión con retroalimentación instantánea.',
    navUpload: '📤 Subir tu texto',
    navLibrary: 'Biblioteca',
    libraryTitle: '📚 Lecturas de ejemplo',
    uploadTitle: '📝 Sube tu propio texto',
    languageLabel: 'Idioma',
    chooseText: 'Elige un texto…',
    choosePart: 'Elige una parte…',
    fragmentHeading: 'Fragmento de la historia',
    questionHeading: 'Pregunta',
    answerPlaceholder: 'Escribe tu respuesta…',
    submitButton: 'Enviar respuesta',
    readAgain: 'Leer otra vez y nuevas preguntas',
    regenerateEasy: 'Preguntas más fáciles',
    regenerateDefault: 'Preguntas estándar',
    strictnessLabel: 'Nivel de evaluación',
    strictness: ['Suave', 'Equilibrado', 'Estricto'],
    audioFragment: 'Escuchar fragmento',
    audioQuestion: 'Escuchar pregunta',
    uppercase: 'MAYÚSCULAS',
    difficultyLabel: 'Estilo de preguntas',
    fragmentToolsTitle: 'Herramientas del fragmento',
    fragmentSize: ['Corto', 'Medio', 'Largo'],
    fragmentPreview: 'Vista previa',
    simplifyTitle: 'Nivel de simplificación',
    simplifyGentle: 'Simplificar texto un poco',
    simplifyGentleHint: 'Hace el texto un poco más fácil de leer manteniendo la mayoría de los detalles',
    simplifyDeep: 'Simplificar texto más',
    simplifyDeepHint: 'Hace el texto mucho más simple, usando vocabulario básico y oraciones más cortas',
    formatButton: 'Limpiar formato',
    formatButtonHint: 'Corrige saltos de línea, espaciado y estructura de párrafos',
    saveButton: 'Guardar en biblioteca',
    pastePlaceholder: 'Pega o escribe tu historia…',
    uploadSuccess: '¡Historia añadida a tu biblioteca!',
    uploadError: 'Error al subir. Inténtalo de nuevo.',
    previewHeading: 'Vista previa de fragmentos',
    previewHint: 'Comprueba cómo se dividirá tu texto en secciones de lectura.',
    noQuestions: 'Aún no hay preguntas. Haz clic en un botón para generar preguntas.',
    questionHint: 'Elige "Preguntas más fáciles" si las actuales son demasiado difíciles.',
    modeLabel: 'Modo',
    modeOriginal: 'Original',
    modeSimple: 'Simplificado',
    toolsLabel: 'Herramientas',
    toolRuler: 'Regla',
    toolSize: 'Tamaño',
    sizeNormal: 'Normal',
    sizeLarge: 'Grande',
    questionTitle: 'Pregunta',
    answerLabel: 'Tu respuesta',
    storyAudio: 'Escuchar historia',
    storyAudioLoading: 'Generando audio…',
    storyAudioError: 'No se pudo generar audio. Inténtalo de nuevo.',
    resultLabel: 'Resultado',
    resultEmpty: 'Responde para ver comentarios aquí.',
    regenerateQuestionsLoading: 'Generando nuevas preguntas…',
    nextQuestion: 'Siguiente pregunta',
    titleLabel: 'Título (opcional)',
    titlePlaceholder: 'Déjalo vacío para generar automáticamente desde las primeras palabras',
    storyCompleted: '🎉 ¡Historia completada!',
    correctAnswers: 'Respuestas correctas',
    startOver: 'Empezar de nuevo',
    textLoadedSuccessfully: '✅ Texto cargado correctamente:',
    fragmentScore: 'Puntuación del fragmento',
    finalScore: 'Puntuación final:',
    generateAllQuestions: 'Generar todas las preguntas',
    generatingAllQuestions: 'Generando preguntas para todos los fragmentos...',
    questionsGenerated: '¡Preguntas generadas para todos los fragmentos!',
  },
  Russian: {
    appTitle: 'Тренер чтения',
    appSubtitle: 'Загрузите текст, упростите его и тренируйте понимание с мгновенной обратной связью.',
    navUpload: '📤 Загрузить текст',
    navLibrary: 'Библиотека',
    libraryTitle: '📚 Примеры из библиотеки',
    uploadTitle: '📝 Загрузите свой текст',
    languageLabel: 'Язык',
    chooseText: 'Выберите текст…',
    choosePart: 'Выберите часть…',
    fragmentHeading: 'Фрагмент истории',
    questionHeading: 'Вопрос',
    answerPlaceholder: 'Введите ответ…',
    submitButton: 'Отправить ответ',
    readAgain: 'Прочитать ещё раз и новые вопросы',
    regenerateEasy: 'Более простые вопросы',
    regenerateDefault: 'Стандартные вопросы',
    strictnessLabel: 'Строгость проверки',
    strictness: ['Мягко', 'Сбалансировано', 'Строго'],
    audioFragment: 'Прослушать фрагмент',
    audioQuestion: 'Прослушать вопрос',
    uppercase: 'ПРОПИСНЫМИ',
    difficultyLabel: 'Стиль вопросов',
    fragmentToolsTitle: 'Инструменты фрагмента',
    fragmentSize: ['Короткие', 'Средние', 'Длинные'],
    fragmentPreview: 'Просмотр фрагментов',
    simplifyTitle: 'Уровень упрощения',
    simplifyGentle: 'Упростить текст немного',
    simplifyGentleHint: 'Делает текст немного легче для чтения, сохраняя большинство деталей',
    simplifyDeep: 'Упростить текст больше',
    simplifyDeepHint: 'Делает текст намного проще, используя базовую лексику и короткие предложения',
    formatButton: 'Очистить форматирование',
    formatButtonHint: 'Исправляет разрывы строк, интервалы и структуру абзацев',
    saveButton: 'Сохранить в библиотеке',
    pastePlaceholder: 'Вставьте или напишите текст…',
    uploadSuccess: 'История добавлена в вашу библиотеку!',
    uploadError: 'Ошибка загрузки. Попробуйте снова.',
    previewHeading: 'Предпросмотр фрагментов',
    previewHint: 'Проверьте, как ваш текст будет разделён на разделы для чтения.',
    noQuestions: 'Пока нет вопросов. Нажмите кнопку, чтобы сгенерировать вопросы.',
    questionHint: 'Выберите «Более простые вопросы», если текущие слишком сложные.',
    modeLabel: 'Режим',
    modeOriginal: 'Оригинал',
    modeSimple: 'Упрощённый',
    toolsLabel: 'Инструменты',
    toolRuler: 'Линейка',
    toolSize: 'Размер',
    sizeNormal: 'Обычный',
    sizeLarge: 'Крупный',
    questionTitle: 'Вопрос',
    answerLabel: 'Ваш ответ',
    storyAudio: 'Слушать историю',
    storyAudioLoading: 'Генерация аудио…',
    storyAudioError: 'Не удалось создать аудио. Попробуйте снова.',
    resultLabel: 'Результат',
    resultEmpty: 'Ответьте, чтобы увидеть отзыв здесь.',
    regenerateQuestionsLoading: 'Генерация новых вопросов…',
    nextQuestion: 'Следующий вопрос',
    titleLabel: 'Название (необязательно)',
    titlePlaceholder: 'Оставьте пустым для автоматической генерации из первых слов',
    storyCompleted: '🎉 История завершена!',
    correctAnswers: 'Правильные ответы',
    startOver: 'Начать заново',
    textLoadedSuccessfully: '✅ Текст загружен успешно:',
    fragmentScore: 'Результат фрагмента',
    finalScore: 'Финальный результат:',
    generateAllQuestions: 'Генерировать все вопросы',
    generatingAllQuestions: 'Генерация вопросов для всех фрагментов...',
    questionsGenerated: 'Вопросы созданы для всех фрагментов!',
  },
}

export function useTranslations(lang: Lang) {
  return dictionary[lang] ?? dictionary.English
}
