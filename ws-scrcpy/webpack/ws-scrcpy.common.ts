import nodeExternals from 'webpack-node-externals';
import fs from 'fs';
import path from 'path';
import webpack from 'webpack';
import MiniCssExtractPlugin from 'mini-css-extract-plugin';
import HtmlWebpackPlugin from 'html-webpack-plugin';
import GeneratePackageJsonPlugin from '@dead50f7/generate-package-json-webpack-plugin';
import { mergeWithDefaultConfig } from './build.config.utils';

export const PROJECT_ROOT = path.resolve(__dirname, '..');
export const SERVER_DIST_PATH = path.join(PROJECT_ROOT, 'dist');
export const CLIENT_DIST_PATH = path.join(PROJECT_ROOT, 'dist/public');
const PACKAGE_JSON = path.join(PROJECT_ROOT, 'package.json');

const override = path.join(PROJECT_ROOT, '/build.config.override.json');
const buildConfigOptions = mergeWithDefaultConfig(override);
const buildConfigDefinePlugin = new webpack.DefinePlugin({
    '__PATHNAME__': JSON.stringify(buildConfigOptions.PATHNAME),
});

export const common = () => {
    return {
        module: {
            rules: [
                {
                    test: /\.css$/i,
                    use: [MiniCssExtractPlugin.loader, 'css-loader'],
                },
                {
                    test: /\.tsx?$/,
                    use: [
                        { loader: 'ts-loader' },
                        {
                            loader: 'ifdef-loader',
                            options: buildConfigOptions,
                        },
                    ],
                    exclude: /node_modules/,
                },
                {
                    test: /\.worker\.js$/,
                    use: { loader: 'worker-loader' },
                },
                {
                    test: /\.svg$/,
                    loader: 'svg-inline-loader',
                },
                {
                    test: /\.(png|jpe?g|gif)$/i,
                    use: [
                        {
                            loader: 'file-loader',
                        },
                    ],
                },
                {
                    test: /\.(asset)$/i,
                    use: [
                        {
                            loader: 'file-loader',
                            options: {
                                name: '[name]',
                            },
                        },
                    ],
                },
                {
                    test: /\.jar$/,
                    use: [
                        {
                            loader: 'file-loader',
                            options: {
                                name: '[path][name].[ext]',
                            },
                        },
                    ],
                },
                {
                    test: /LICENSE/i,
                    use: [
                        {
                            loader: 'file-loader',
                            options: {
                                name: '[path][name]',
                            },
                        },
                    ],
                },
            ],
        },
        resolve: {
            extensions: ['.tsx', '.ts', '.js'],
        },
    };
};

const front: webpack.Configuration = {
    entry: path.join(PROJECT_ROOT, './src/app/index.ts'),
    externals: ['fs'],
    plugins: [
        new HtmlWebpackPlugin({
            template: path.join(PROJECT_ROOT, '/src/public/index.html'),
            inject: 'head',
        }),
        new MiniCssExtractPlugin(),
        new webpack.ProvidePlugin({
            Buffer: ['buffer', 'Buffer'],
        }),
    ],
    resolve: {
        fallback: {
            path: 'path-browserify',
        },
        extensions: ['.tsx', '.ts', '.js'],
    },
    output: {
        filename: 'bundle.js',
        path: CLIENT_DIST_PATH,
    },
};

export const frontend = () => {
    return Object.assign({}, common(), front);
};

const packageJson = JSON.parse(fs.readFileSync(PACKAGE_JSON).toString());
const { name, version, description, author, license, scripts } = packageJson;
const basePackage = {
    name,
    version,
    description,
    author,
    license,
    scripts: { start: scripts['script:dist:start'] },
    pkg: {
        assets: [
            'public/**/*',
            'vendor/**/*',
            'LICENSE'
        ],
        targets: [
            'node18-linux-x64'
        ],
        outputPath: '.'
    }
};
delete packageJson.dependencies;
delete packageJson.devDependencies;

// Módulos nativos que deben copiarse después del build (no pueden ser empaquetados)
const nativeModulesToCopy = ['node-pty', 'ios-device-lib'];

// Plugin personalizado para copiar módulos nativos después del build
class CopyNativeModulesPlugin {
    apply(compiler: webpack.Compiler) {
        compiler.hooks.afterEmit.tap('CopyNativeModulesPlugin', () => {
            nativeModulesToCopy.forEach(moduleName => {
                const sourcePath = path.join(PROJECT_ROOT, 'node_modules', moduleName);
                const destPath = path.join(SERVER_DIST_PATH, 'node_modules', moduleName);
                
                if (fs.existsSync(sourcePath)) {
                    // Crear directorio destino si no existe
                    if (!fs.existsSync(path.dirname(destPath))) {
                        fs.mkdirSync(path.dirname(destPath), { recursive: true });
                    }
                    
                    // Copiar módulo completo
                    this.copyRecursiveSync(sourcePath, destPath);
                }
            });
        });
    }
    
    private copyRecursiveSync(src: string, dest: string) {
        const exists = fs.existsSync(src);
        const stats = exists && fs.statSync(src);
        const isDirectory = exists && stats && stats.isDirectory();
        
        if (isDirectory) {
            if (!fs.existsSync(dest)) {
                fs.mkdirSync(dest, { recursive: true });
            }
            fs.readdirSync(src).forEach(childItemName => {
                // Excluir archivos de desarrollo
                if (childItemName === 'test' || childItemName === 'tests' || 
                    childItemName === '.git' || childItemName.endsWith('.md') ||
                    childItemName === 'tsconfig.json') {
                    return;
                }
                this.copyRecursiveSync(
                    path.join(src, childItemName),
                    path.join(dest, childItemName)
                );
            });
        } else {
            fs.copyFileSync(src, dest);
        }
    }
}

const back: webpack.Configuration = {
    entry: path.join(PROJECT_ROOT, './src/server/index.ts'),
    externals: [
        // Incluir TODAS las dependencias de node_modules en el bundle
        // EXCEPTO los módulos nativos que se copiarán manualmente
        nodeExternals({
            importType: 'commonjs',
            // allowlist: función que retorna true para INCLUIR en bundle, false para EXCLUIR
            // Por defecto, incluir TODAS las dependencias y sus subdependencias
            // Solo excluir módulos nativos específicos
            allowlist: (moduleName: string) => {
                // Obtener el nombre base del módulo (sin subcarpetas)
                const baseModuleName = moduleName.split('/')[0];
                
                // Si es un módulo nativo, EXCLUIRLO del bundle (retornar false)
                // Estos se copiarán manualmente después del build
                if (nativeModulesToCopy.includes(baseModuleName)) {
                    return false;
                }
                
                // Para TODOS los demás módulos (incluyendo subdependencias como body-parser),
                // INCLUIRLOS en el bundle (retornar true)
                // Esto asegura que todas las subdependencias se empaqueten correctamente
                return true;
            },
        })
    ],
    plugins: [
        new GeneratePackageJsonPlugin(basePackage),
        buildConfigDefinePlugin,
        // Copiar módulos nativos necesarios para tiempo de ejecución
        new CopyNativeModulesPlugin(),
    ],
    // Suprimir warnings inofensivos que no afectan la funcionalidad
    ignoreWarnings: [
        // Warning de Express sobre dependencias dinámicas (común y seguro)
        {
            module: /express\/lib\/view\.js/,
            message: /Critical dependency: the request of a dependency is an expression/,
        },
        // Módulos opcionales de ws que mejoran rendimiento pero no son requeridos
        {
            module: /ws\/lib\/buffer-util\.js/,
            message: /Can't resolve 'bufferutil'/,
        },
        {
            module: /ws\/lib\/validation\.js/,
            message: /Can't resolve 'utf-8-validate'/,
        },
    ],
    node: {
        global: false,
        __filename: false,
        __dirname: false,
    },
    output: {
        filename: 'index.js',
        path: SERVER_DIST_PATH,
    },
    target: 'node',
};

export const backend = () => {
    return Object.assign({}, common(), back);
};
