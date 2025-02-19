from wasmtime import Store, Module, Instance, Linker, WasiConfig, Caller

# Создаем хранилище и настраиваем WASI
store = Store()
wasi_config = WasiConfig()
store.set_wasi(wasi_config)

# Загружаем скомпилированный .wasm файл
module = Module.from_file(store.engine, 'wikidot_normalize.wasm')

# Создаем линкер и добавляем поддержку WASI
linker = Linker(store.engine)
linker.define_wasi()

# Создаем экземпляр модуля с использованием линкера
instance = linker.instantiate(store, module)

# Получаем функцию 'add' из экспортов модуля
exports = instance.exports(store)
print([export for export in exports])

normalize_string = exports["normalize_string"]
print(type(normalize_string))
# Вызываем функцию 'add'
input_value = "Лисодевочки"
output = ""
result = normalize_string(store, input_value, output)
print(f'Result: {input_value} => {result}')  # Ожидаемый вывод: Result: 12
